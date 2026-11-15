from django.db import migrations, models
from django.db.models import Count
from django.db.models.functions import Lower


def validate_existing_emails(apps, schema_editor):
    CustomUser = apps.get_model("accounts", "CustomUser")
    database = schema_editor.connection.alias
    duplicate_emails = (
        CustomUser.objects.using(database)
        .exclude(email="")
        .annotate(normalized_email=Lower("email"))
        .values("normalized_email")
        .annotate(total=Count("pk"))
        .filter(total__gt=1)
    )
    if duplicate_emails.exists():
        raise RuntimeError(
            "Cannot enforce unique user emails: duplicate non-empty email addresses "
            "exist. Resolve them before applying this migration."
        )


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(validate_existing_emails, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(
                Lower("email"),
                condition=~models.Q(email=""),
                name="user_email_ci_uniq",
                violation_error_message="A user with this email already exists.",
            ),
        ),
    ]
