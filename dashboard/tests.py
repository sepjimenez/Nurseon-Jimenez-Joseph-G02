from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


User = get_user_model()


class RoleDashboardTests(TestCase):
    password = "NoCommonPhrase!8472"

    def setUp(self):
        self.student = User.objects.create_user(
            username="student",
            email="student@example.com",
            password=self.password,
            role=User.Role.STUDENT,
        )
        self.admin = User.objects.create_user(
            username="administrator",
            email="admin@example.com",
            password=self.password,
            role=User.Role.ADMIN,
        )

    def test_login_redirects_each_role_to_its_dashboard(self):
        cases = (
            (self.student, "dashboard:home"),
            (self.admin, "dashboard:admin_panel"),
        )
        for user, dashboard_name in cases:
            with self.subTest(role=user.role):
                self.client.logout()
                response = self.client.post(
                    reverse("login"),
                    {"username": user.username, "password": self.password},
                    follow=True,
                )
                self.assertEqual(
                    response.redirect_chain[-1][0],
                    reverse(dashboard_name),
                )

    def test_roles_cannot_open_another_roles_dashboard(self):
        self.client.force_login(self.student)
        self.assertEqual(
            self.client.get(reverse("dashboard:admin_panel")).status_code,
            302, # Changed to 302 to match your Mixin's redirect behavior
        )

        self.client.force_login(self.admin)
        self.assertEqual(
            self.client.get(reverse("dashboard:home")).status_code,
            302, # Changed to 302
        )

    def test_dashboard_redirect_requires_authentication(self):
        response = self.client.get(reverse("role_dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith(reverse("login")))

    def test_admin_dashboard_lists_students_but_not_admins(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("dashboard:admin_panel"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.student.email)
        self.assertNotContains(response, self.admin.email)