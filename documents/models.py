import re
from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class NursingDocument(models.Model):
    doc_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="Custom or system identifier (e.g. doc_01)",
    )
    title = models.CharField(max_length=255)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
    )
    read_time = models.CharField(
        max_length=50,
        default="10 mins (estimated)",
        help_text="e.g. 12 mins (estimated)",
    )
    description = models.TextField(
        help_text="Summary or overview of the nursing document"
    )
    publish_date = models.DateField(default=timezone.now)
    is_published = models.BooleanField(
        default=True,
        help_text="Whether this document is visible to students",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="nursing_documents",
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name="documents")
    bookmarks = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="bookmarked_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-publish_date", "-created_at"]

    def __str__(self):
        return f"{self.doc_id or self.pk}: {self.title}"

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.doc_id:
                last = (
                    NursingDocument.objects.filter(doc_id__startswith="doc_")
                    .order_by("-id")
                    .first()
                )
                if last and last.doc_id:
                    match = re.search(r"doc_(\d+)", last.doc_id)
                    next_num = int(match.group(1)) + 1 if match else 1
                else:
                    next_num = 1

                candidate = f"doc_{next_num:02d}"
                while NursingDocument.objects.filter(doc_id=candidate).exists():
                    next_num += 1
                    candidate = f"doc_{next_num:02d}"
                self.doc_id = candidate
            super().save(*args, **kwargs)

    def can_view(self, user):
        """
        Admins can view all records.
        Authors can view their own records.
        Staff/Admin authored public documents can be viewed by all students.
        Other students' documents are private to the creator.
        """
        if not user.is_authenticated:
            return False
        if user.is_admin_role():
            return True
        if self.created_by_id == user.pk:
            return True
        # If created by admin/staff, visible to enrolled students
        if self.created_by.is_admin_role() and self.is_published:
            return True
        return False

    def can_modify(self, user):
        """
        Only the creator or an administrator can update or delete.
        """
        if not user.is_authenticated:
            return False
        if user.is_admin_role():
            return True
        return self.created_by_id == user.pk


class DocumentSection(models.Model):
    SECTION_TYPES = [
        ("paragraph", "Paragraph"),
        ("heading", "Heading"),
        ("callout", "Key Callout"),
    ]
    document = models.ForeignKey(
        NursingDocument,
        on_delete=models.CASCADE,
        related_name="content_sections",
    )
    order = models.PositiveIntegerField(default=0)
    section_type = models.CharField(
        max_length=20,
        choices=SECTION_TYPES,
        default="paragraph",
    )
    text = models.TextField()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.document.doc_id} Section {self.order} ({self.section_type})"


class DocumentSource(models.Model):
    document = models.ForeignKey(
        NursingDocument,
        on_delete=models.CASCADE,
        related_name="sources",
    )
    order = models.PositiveIntegerField(default=0)
    text = models.TextField()

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.document.doc_id} Source #{self.order}"


def visible_documents_for(user):
    documents = NursingDocument.objects.select_related(
        "category", "created_by"
    ).prefetch_related("tags")
    if user.is_admin_role():
        return documents
    return documents.filter(
        Q(created_by=user)
        | Q(created_by__role="ADMIN", is_published=True)
    ).distinct()
