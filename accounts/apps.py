from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self):
        def _post_migrate_admin_sync(sender, **kwargs):
            from django.conf import settings
            if getattr(settings, "TESTING", False):
                return
            from .admin_setup import sync_admin_account
            sync_admin_account(wipe_old_admins=False)

        post_migrate.connect(_post_migrate_admin_sync, sender=self)
