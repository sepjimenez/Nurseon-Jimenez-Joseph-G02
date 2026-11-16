import warnings

from django.conf import settings
from django.db import migrations

from documents.seed_data import seed_nursing_ethics_document


def seed_initial_document(apps, schema_editor):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    User = apps.get_model(app_label, model_name)
    database = schema_editor.connection.alias
    author = User.objects.using(database).filter(role="ADMIN").order_by("pk").first()
    if author is None:
        warnings.warn(
            "The initial nursing document was not seeded because no administrator "
            "account exists. Run `python manage.py seed_documents` after creating one.",
            RuntimeWarning,
            stacklevel=2,
        )
        return

    seed_nursing_ethics_document(apps, database, author)


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(
            seed_initial_document,
            migrations.RunPython.noop,
        ),
    ]
