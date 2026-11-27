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

    def test_login_required_for_document_views(self):
        protected_urls = [
            reverse("documents:list"),
            reverse("documents:detail", args=[self.public_document.pk]),
            reverse("documents:bookmark", args=[self.public_document.pk]),
        ]
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 302)
                self.assertIn(reverse("login"), response.url)

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

    def test_library_rejects_invalid_filter_inputs_gracefully(self):
        self.client.force_login(self.student)

        response = self.client.get(
            reverse("documents:list"),
            {"q": "x" * 150, "category": "nonexistent-category"},
        )

        self.assertEqual(response.status_code, 200)
        messages = list(response.context["messages"])
        self.assertTrue(len(messages) >= 1)

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

    def test_students_cannot_read_unpublished_or_missing_documents(self):
        self.client.force_login(self.student)

        unpublished_response = self.client.get(
            reverse("documents:detail", args=[self.unpublished_document.pk])
        )
        missing_response = self.client.get(
            reverse("documents:detail", args=[999999])
        )

        self.assertEqual(unpublished_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)

    def test_bookmark_requires_post_and_toggles_cleanly(self):
        self.client.force_login(self.student)
        url = reverse("documents:bookmark", args=[self.public_document.pk])

        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 405)

        add_response = self.client.post(url)
        self.assertRedirects(
            add_response,
            reverse("documents:detail", args=[self.public_document.pk]),
        )
        self.assertTrue(self.public_document.bookmarks.filter(pk=self.student.pk).exists())

        remove_response = self.client.post(url)
        self.assertRedirects(
            remove_response,
            reverse("documents:detail", args=[self.public_document.pk]),
        )
        self.assertFalse(self.public_document.bookmarks.filter(pk=self.student.pk).exists())

    def test_doc_id_auto_generation_avoids_collisions(self):
        existing = NursingDocument.objects.create(
            doc_id="doc_99",
            title="Manual ID doc",
            description="Occupies doc_99.",
            created_by=self.admin,
        )
        self.assertEqual(existing.doc_id, "doc_99")

        auto_doc = NursingDocument.objects.create(
            title="Next auto doc",
            description="Should skip doc_99 to doc_100.",
            created_by=self.admin,
        )
        self.assertEqual(auto_doc.doc_id, "doc_100")


    def test_deleting_user_does_not_delete_documents(self):
        # User creates a doc
        doc = NursingDocument.objects.create(
            title="Survivor doc",
            description="This should survive user deletion.",
            created_by=self.student,
        )
        
        # Delete the user
        self.student.delete()
        
        # Verify document still exists and created_by is null
        doc.refresh_from_db()
        self.assertIsNone(doc.created_by)
        self.assertEqual(NursingDocument.objects.filter(pk=doc.pk).count(), 1)