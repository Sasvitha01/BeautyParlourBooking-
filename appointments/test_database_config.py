"""
Database URL parsing and configuration tests using dummy credentials.
Verifies that all bracketed/malformed URL patterns from Supabase / Render
are correctly sanitized and parsed without throwing ValueError or crash.
"""
from django.test import SimpleTestCase
from glownest.settings import sanitize_database_url
import dj_database_url


class DatabaseUrlParsingTests(SimpleTestCase):
    def test_bracketed_hostname_sanitization(self):
        url = "postgresql://dummy_user:dummy_pass@[aws-0-ap-northeast-1.pooler.supabase.com]:6543/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['ENGINE'], 'django.db.backends.postgresql')
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')
        self.assertEqual(cfg['PORT'], 6543)
        self.assertEqual(cfg['USER'], 'dummy_user')
        self.assertEqual(cfg['PASSWORD'], 'dummy_pass')
        self.assertEqual(cfg['NAME'], 'postgres')

    def test_bracketed_hostname_and_port(self):
        url = "postgresql://dummy_user:dummy_pass@[aws-0-ap-northeast-1.pooler.supabase.com:6543]/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')
        self.assertEqual(cfg['PORT'], 6543)

    def test_bracketed_password_sanitization(self):
        # Reproduces Supabase placeholder template or user password wrapped in brackets
        url = "postgresql://dummy_user:[dummy_secret_pass]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://dummy_user:dummy_secret_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['USER'], 'dummy_user')
        self.assertEqual(cfg['PASSWORD'], 'dummy_secret_pass')
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

    def test_both_bracketed_password_and_bracketed_host(self):
        url = "postgresql://dummy_user:[dummy_pass]@[aws-0-ap-northeast-1.pooler.supabase.com]:5432/postgres"
        clean = sanitize_database_url(url)
        # Port 5432 is automatically routed to transaction mode port 6543
        self.assertEqual(clean, "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')
        self.assertEqual(cfg['PORT'], 6543)

    def test_quoted_and_whitespace_url(self):
        url = '  "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"  '
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

    def test_placeholder_password_warning_handled(self):
        url = "postgresql://postgres.testref:[YOUR-PASSWORD]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://postgres.testref:YOUR-PASSWORD@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['USER'], 'postgres.testref')
        self.assertEqual(cfg['PASSWORD'], 'YOUR-PASSWORD')

    def test_genuine_ipv6_preserved(self):
        url = "postgresql://dummy_user:dummy_pass@[2001:db8::1]:5432/postgres"
        clean = sanitize_database_url(url)
        # Bracketed IPv6 should not have brackets stripped
        self.assertIn("[2001:db8::1]", clean)

    def test_bracketed_supabase_project_ref_in_username(self):
        # Common Supabase template: postgres.[project-ref]:password
        url = "postgresql://postgres.[myprojectref]:my_secret_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://postgres.myprojectref:my_secret_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['USER'], 'postgres.myprojectref')
        self.assertEqual(cfg['PASSWORD'], 'my_secret_pass')
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

    def test_bracketed_user_and_bracketed_password(self):
        # Both project-ref and password in brackets from copy-paste
        url = "postgresql://postgres.[myprojectref]:[my_secret_pass]@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres"
        clean = sanitize_database_url(url)
        self.assertEqual(clean, "postgresql://postgres.myprojectref:my_secret_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['USER'], 'postgres.myprojectref')
        self.assertEqual(cfg['PASSWORD'], 'my_secret_pass')
        self.assertEqual(cfg['PORT'], 6543)

    def test_password_with_special_characters_and_brackets(self):
        # Passwords containing @ or # or literal brackets
        url = "postgresql://dummy_user:[pass@123#]@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres"
        clean = sanitize_database_url(url)
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['USER'], 'dummy_user')
        self.assertEqual(cfg['PASSWORD'], 'pass@123#')
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

    def test_angle_brackets_and_outer_square_brackets(self):
        # User copied URL from documentation with <...> or [...]
        url1 = "<postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres>"
        clean1 = sanitize_database_url(url1)
        cfg1 = dj_database_url.parse(clean1, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg1['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

        url2 = "[postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/postgres]"
        clean2 = sanitize_database_url(url2)
        cfg2 = dj_database_url.parse(clean2, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg2['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

    def test_bracketed_database_name(self):
        url = "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:6543/[postgres]"
        clean = sanitize_database_url(url)
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['NAME'], 'postgres')
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')

