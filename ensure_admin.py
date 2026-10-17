"""
Script to ensure an active admin superuser exists on both local and production (Supabase) databases.
Never overwrites an existing user's password unless explicitly requested via RESET_ADMIN_PASSWORD=true.
Never uses hardcoded default passwords.
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
    new_password = os.getenv('ADMIN_PASSWORD', '').strip()
    force_reset = os.getenv('RESET_ADMIN_PASSWORD', '').lower() in ('true', '1', 'yes')

    if not username:
        print("[GlowNest] Admin username empty, skipping ensure_admin.")
        return

    try:
        user = User.objects.filter(username=username).first()
        if user:
            if force_reset and new_password:
                user.set_password(new_password)
                user.is_staff = True
                user.is_superuser = True
                user.is_active = True
                user.save()
                print(f"[GlowNest] Successfully reset password for existing superuser '{username}'.")
                return

            print(f"[GlowNest] Admin user '{username}' already exists. Preserving existing password.")
            needs_save = False
            if not user.is_staff:
                user.is_staff = True
                needs_save = True
            if not user.is_superuser:
                user.is_superuser = True
                needs_save = True
            if not user.is_active:
                user.is_active = True
                needs_save = True
            if needs_save:
                user.save(update_fields=['is_staff', 'is_superuser', 'is_active'])
            return

        # User does not exist: only create if ADMIN_PASSWORD is provided in environment
        if not new_password:
            print(
                f"[GlowNest] Superuser '{username}' does not exist and no ADMIN_PASSWORD environment "
                f"variable is set. You can create an admin using: python manage.py createsuperuser"
            )
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=new_password,
        )
        print(f"[GlowNest] Successfully created initial superuser '{username}'.")
    except Exception as e:
        print(f"[GlowNest] Warning: Could not ensure admin user: {e}", file=sys.stderr)

if __name__ == '__main__':
    ensure_admin()
