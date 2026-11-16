from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, DocumentSection, DocumentSource, NursingDocument, Tag


User = get_user_model()


class DocumentLibraryTests(TestCase):
    password = "NoCommonPhrase!8472"

    def setUp(self):
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password=self.password,
            role=User.Role.STUDENT,
        )
        self.other_student = User.objects.create_user(
            username="other",
            email="other@example.com",
            password=self.password,
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="administrator",
            email="admin@example.com",
            password=self.password,
            role=User.Role.ADMIN,
        )
        self.category = Category.objects.create(name="Fundamentals")
        self.tag = Tag.objects.create(name="Patient Safety")
        self.public_document = NursingDocument.objects.create(
            title="Patient safety essentials",
            description="A guide to safe nursing practice.",
            category=self.category,
            created_by=self.admin,
        )
        self.public_document.tags.add(self.tag)
        self.private_document = NursingDocument.objects.create(
            title="Private student notes",
            description="Personal study notes.",
            created_by=self.other_student,
        )
        self.unpublished_document = NursingDocument.objects.create(
            title="Unpublished reference",
            description="Not ready for students.",
            created_by=self.admin,
            is_published=False,
        )

    def test_dashboard_displays_recent_documents_and_link_to_library(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("dashboard:home"))

        self.assertContains(response, self.public_document.title)
        self.assertContains(response, reverse("documents:list"))
        self.assertNotContains(response, self.private_document.title)
        self.assertNotContains(response, self.unpublished_document.title)

    def test_library_searches_document_tags(self):
        self.client.force_login(self.student)

        response = self.client.get(reverse("documents:list"), {"q": "Patient Safety"})

        self.assertContains(response, self.public_document.title)
        self.assertNotContains(response, self.private_document.title)

    def test_library_filters_by_category(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("documents:list"),
            {"category": self.category.slug},
        )

        self.assertContains(response, self.public_document.title)
        self.assertNotContains(response, self.private_document.title)

    def test_document_detail_renders_sections_and_sources(self):
        DocumentSection.objects.create(
            document=self.public_document,
            section_type="heading",
            text="Core principles",
        )
        DocumentSource.objects.create(
            document=self.public_document,
            order=1,
            text="Nursing practice reference",
        )
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("documents:detail", args=[self.public_document.pk])
        )

        self.assertContains(response, "Core principles")
        self.assertContains(response, "Nursing practice reference")

    def test_students_cannot_read_other_students_private_documents(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("documents:detail", args=[self.private_document.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_bookmark_can_be_added_and_removed(self):
        self.client.force_login(self.student)
        url = reverse("documents:bookmark", args=[self.public_document.pk])

        add_response = self.client.post(url)
        self.assertRedirects(
            add_response,
            reverse("documents:detail", args=[self.public_document.pk]),
        )
        self.assertTrue(self.public_document.bookmarks.filter(pk=self.student.pk).exists())

        self.client.post(url)
        self.assertFalse(self.public_document.bookmarks.filter(pk=self.student.pk).exists())
