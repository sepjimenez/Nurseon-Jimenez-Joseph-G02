from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.functions import Lower

class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'STUDENT', 'Student'
        ADMIN = 'ADMIN', 'Administrator'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT
    )
    specialization = models.CharField(max_length=100, blank=True, default="General Nursing")
    password_reset_requested_at = models.DateTimeField(null=True, blank=True)

    class Meta(AbstractUser.Meta):
        abstract = False
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                condition=~Q(email=""),
                name="user_email_ci_uniq",
                violation_error_message="A user with this email already exists.",
            ),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"

    def is_admin_role(self):
        return self.role == self.Role.ADMIN

    def save(self, *args, **kwargs):
        is_admin = self.role == self.Role.ADMIN
        self.is_staff = is_admin
        self.is_superuser = is_admin
        update_fields = kwargs.get("update_fields")
        if update_fields is not None:
            kwargs["update_fields"] = {*update_fields, "is_staff", "is_superuser"}
        super().save(*args, **kwargs)

    def can_be_deleted_by(self, user):
        if self.pk == user.pk:
            return False, "You cannot delete your own account."
        if self.role == self.Role.ADMIN:
            admin_count = CustomUser.objects.filter(role=self.Role.ADMIN).count()
            if admin_count <= 1:
                return False, "Cannot delete the only remaining administrator."
        return True, ""

    def can_be_demoted_by(self, user):
        if self.pk == user.pk:
            return False, "You cannot demote your own account from Administrator."
        if self.role == self.Role.ADMIN:
            admin_count = CustomUser.objects.filter(role=self.Role.ADMIN).count()
            if admin_count <= 1:
                return False, "Cannot demote the only remaining administrator."
        return True, ""

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def icon_type(self):
        spec = (self.specialization or '').lower()
        if 'pediatric' in spec or 'baby' in spec:
            return 'pediatrics'
        elif 'tech' in spec or 'micro' in spec:
            return 'med-tech'
        elif 'pharm' in spec or 'pill' in spec:
            return 'pharma'
        return 'med-surg'
