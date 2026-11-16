from django.apps import apps
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from documents.seed_data import seed_nursing_ethics_document


class Command(BaseCommand):
    help = "Seed the initial nursing documents."

    def add_arguments(self, parser):
        parser.add_argument(
            "--database",
            default=DEFAULT_DB_ALIAS,
            help="The database to seed.",
        )

    def handle(self, *args, **options):
        database = options["database"]
        User = get_user_model()
        author = (
            User.objects.using(database)
            .filter(role=User.Role.ADMIN)
            .order_by("pk")
            .first()
        )
        if author is None:
            raise CommandError(
                "Create an administrator account before seeding nursing documents."
            )

        document, created = seed_nursing_ethics_document(apps, database, author)
        action = "Created" if created else "Already present"
        self.stdout.write(
            self.style.SUCCESS(f"{action} {document.doc_id}: {document.title}")
        )
