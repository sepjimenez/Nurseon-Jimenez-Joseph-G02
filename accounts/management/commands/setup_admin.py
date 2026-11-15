from django.core.management.base import BaseCommand
from accounts.admin_setup import sync_admin_account

class Command(BaseCommand):
    help = "Removes prior admin accounts and creates a new admin using ADMIN_EMAIL and ADMIN_PASSWORD from .env"

    def handle(self, *args, **options):
        self.stdout.write("Synchronizing administrator account from environment...")
        success, message = sync_admin_account()
        if success:
            self.stdout.write(self.style.SUCCESS(message))
        else:
            self.stdout.write(self.style.ERROR(message))

