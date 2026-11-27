from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction, connection
from django.test import TestCase
from django.urls import reverse

from .forms import CustomUserCreationForm


User = get_user_model()


class RegistrationTests(TestCase):
    password = "NoCommonPhrase!8472"

    def registration_data(self, **overrides):
        data = {
            "username": "newstudent",
            "email": "newstudent@example.com",
            "password1": self.password,
            "password2": self.password,
        }
        data.update(overrides)
        return data

    def test_registration_requires_valid_email(self):
        for email in ("", "not-an-email"):
            with self.subTest(email=email):
                form = CustomUserCreationForm(data=self.registration_data(email=email))
                self.assertFalse(form.is_valid())
                self.assertIn("email", form.errors)

    def test_registration_rejects_case_insensitive_duplicate_email(self):
        User.objects.create_user(
            username="existing",
            email="Existing@example.com",
            password=self.password,
        )

        form = CustomUserCreationForm(
            data=self.registration_data(email="existing@EXAMPLE.com")
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_email_uniqueness_is_enforced_by_database(self):
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password=self.password,
        )

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    username="duplicate",
                    email="EXISTING@example.com",
                    password=self.password,
                )

    def test_registration_assigns_student_and_hashes_password(self):
        response = self.client.post(
            reverse("signup"),
            self.registration_data(role=User.Role.ADMIN),
            follow=True,
        )

        user = User.objects.get(username="newstudent")
        self.assertEqual(user.role, User.Role.STUDENT)
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))
        self.assertContains(response, "Account created successfully")

    def test_registration_form_does_not_expose_role(self):
        self.assertNotIn("role", CustomUserCreationForm.base_fields)

    def test_profile_requires_authentication_and_updates_current_user(self):
        user = User.objects.create_user(
            username="profile-owner",
            email="owner@example.com",
            password=self.password,
        )
        other_user = User.objects.create_user(
            username="other-user",
            email="other@example.com",
            password=self.password,
        )

        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(user)
        response = self.client.post(
            reverse("profile"),
            {
                "username": "profile-owner",
                "email": "owner@example.com",
                "first_name": "Updated",
                "last_name": "",
                "specialization": "Pediatrics",
            },
        )

        self.assertEqual(response.status_code, 302)
        user.refresh_from_db()
        other_user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(other_user.first_name, "")


class AdminStudentManagementTests(TestCase):
    password = "NoCommonPhrase!8472"

    def setUp(self):
        self.admin = User.objects.create_user(
            username="administrator",
            email="admin@example.com",
            password=self.password,
            role=User.Role.ADMIN,
        )
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password=self.password,
            role=User.Role.STUDENT,
        )
        self.client.force_login(self.admin)

    def test_admin_can_update_student_credentials_and_role(self):
        response = self.client.post(
            reverse("admin_student_edit", args=[self.student.pk]),
            {
                "username": "updated-student",
                "email": "updated@example.com",
                "first_name": "Updated",
                "last_name": "Student",
                "specialization": "Pediatrics",
                "role": User.Role.ADMIN,
            },
        )

        self.assertRedirects(response, reverse("dashboard:admin_panel"))
        self.student.refresh_from_db()
        self.assertEqual(self.student.username, "updated-student")
        self.assertEqual(self.student.email, "updated@example.com")
        self.assertEqual(self.student.role, User.Role.ADMIN)

    def test_admin_can_delete_student(self):
        response = self.client.post(
            reverse("admin_student_delete", args=[self.student.pk]),
            follow=True,
        )

        # Check the messages directly in the context
        messages = [str(m) for m in response.context['messages']]
        self.assertTrue(any("was deleted successfully" in m for m in messages))
        
        self.assertFalse(User.objects.filter(pk=self.student.pk).exists())
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_non_admin_cannot_manage_students(self):
        self.client.force_login(self.student)
        response = self.client.get(
            reverse("admin_student_edit", args=[self.student.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_management_cannot_target_another_admin(self):
        other_admin = User.objects.create_user(
            username="other-admin",
            email="other-admin@example.com",
            password=self.password,
            role=User.Role.ADMIN,
        )

        edit_response = self.client.get(
            reverse("admin_student_edit", args=[other_admin.pk])
        )
        delete_response = self.client.get(
            reverse("admin_student_delete", args=[other_admin.pk])
        )

        self.assertEqual(edit_response.status_code, 404) 
        self.assertEqual(delete_response.status_code, 404)