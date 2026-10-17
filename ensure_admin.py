"""
Script to ensure an active admin superuser exists on both local and production (Supabase) databases.
Can read credentials from environment variables ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD
or fall back to the project default.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'glownest.settings')
django.setup()

from django.contrib.auth import get_user_model

def ensure_admin():
    User = get_user_model()
    username = os.getenv('ADMIN_USERNAME', 'admin').strip()
    email = os.getenv('ADMIN_EMAIL', 'admin@glownest.com').strip()
    password = os.getenv('ADMIN_PASSWORD', 'GlowNestAdmin2026!').strip()

    if not username or not password:
        print("[GlowNest] Admin username or password empty, skipping ensure_admin.")
        return

    try:
        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()

        if created:
            print(f"[GlowNest] Successfully created superuser '{username}'.")
        else:
            print(f"[GlowNest] Successfully updated password for superuser '{username}'.")
    except Exception as e:
        print(f"[GlowNest] Warning: Could not ensure admin user: {e}", file=sys.stderr)

if __name__ == '__main__':
    ensure_admin()
