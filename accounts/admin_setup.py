import os
import logging
from django.db import transaction

logger = logging.getLogger(__name__)

def sync_admin_account(wipe_old_admins=True):
    """
    Synchronizes the administrator account using ADMIN_EMAIL, ADMIN_PASSWORD,
    and ADMIN_USERNAME from the environment (.env).
    Removes prior legacy admin accounts to ensure clean credential management
    and prevent lockout.
    """
    from accounts.models import CustomUser

    admin_email = os.getenv("ADMIN_EMAIL", "").strip()
    admin_password = os.getenv("ADMIN_PASSWORD", "").strip()
    admin_username = os.getenv("ADMIN_USERNAME", "admin").strip()

    if not admin_email or not admin_password:
        return False, "ADMIN_EMAIL and ADMIN_PASSWORD must be set in .env"

    try:
        with transaction.atomic():
            if wipe_old_admins:
                # Remove prior legacy admin accounts
                CustomUser.objects.filter(role=CustomUser.Role.ADMIN).exclude(
                    username__iexact=admin_username
                ).exclude(
                    email__iexact=admin_email
                ).delete()

            # Find existing user by username or email
            admin_user = CustomUser.objects.filter(username__iexact=admin_username).first()
            if not admin_user:
                admin_user = CustomUser.objects.filter(email__iexact=admin_email).first()

            if admin_user:
                admin_user.username = admin_username
                admin_user.email = admin_email
                admin_user.role = CustomUser.Role.ADMIN
                admin_user.is_staff = True
                admin_user.is_superuser = True
                admin_user.set_password(admin_password)
                admin_user.specialization = "Administration"
                admin_user.save()
            else:
                admin_user = CustomUser.objects.create_superuser(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    role=CustomUser.Role.ADMIN,
                    specialization="Administration",
                )
            return True, f"Admin account '{admin_user.username}' ({admin_email}) synchronized successfully."
    except Exception as exc:
        logger.exception("Failed to sync admin account: %s", exc)
        return False, str(exc)
