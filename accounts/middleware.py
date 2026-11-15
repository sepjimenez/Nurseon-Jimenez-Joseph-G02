import logging
from .admin_setup import sync_admin_account

logger = logging.getLogger(__name__)
_ADMIN_SYNCED = False

class AutoSyncAdminMiddleware:
    """
    Ensures the administrator account configured in .env (ADMIN_EMAIL, ADMIN_PASSWORD)
    is synchronized automatically in the database on the first request without requiring
    manual command line execution.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _ADMIN_SYNCED
        if not _ADMIN_SYNCED:
            try:
                success, msg = sync_admin_account(wipe_old_admins=True)
                if success:
                    _ADMIN_SYNCED = True
                    logger.info("Admin sync: %s", msg)
            except Exception as e:
                logger.error("AutoSyncAdminMiddleware error: %s", e)
        return self.get_response(request)

