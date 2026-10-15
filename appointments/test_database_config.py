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
        self.assertEqual(clean, "postgresql://dummy_user:dummy_pass@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres")
        cfg = dj_database_url.parse(clean, conn_max_age=0, conn_health_checks=True, ssl_require=True)
        self.assertEqual(cfg['HOST'], 'aws-0-ap-northeast-1.pooler.supabase.com')
        self.assertEqual(cfg['PORT'], 5432)

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
