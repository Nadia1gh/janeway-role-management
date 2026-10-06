from django.test import TestCase, override_settings
from django.urls import reverse

from rest_framework.test import APIClient

from utils.testing import helpers
from core import models as core_models


class TestAPI(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.press = helpers.create_press()
        cls.journal, _ = helpers.create_journals()
        cls.staff_member = helpers.create_user(
            username="t.paris@voyager.com",
            roles=["author"],
            journal=cls.journal,
            is_staff=True,
            is_active=True,
        )
        cls.editor = helpers.create_user(
            username="h.kim@voyager.com",
            roles=["editor"],
            journal=cls.journal,
            is_active=True,
        )
        cls.average_user = helpers.create_user(
            "a.redshirt@voyager.com",
            roles=["author"],
            journal=cls.journal,
            is_active=True,
        )
        helpers.create_roles(
            [
                "journal-manager",
                "reviewer",
            ],
        )
        cls.api_client = APIClient()

    @override_settings(URL_CONFIG="domain")
    def test_staff_member_can_assign_journal_manager_role(self):
        self.api_client.force_authenticate(user=self.staff_member)
        url = self.journal.site_url(
            reverse(
                "accountrole-list",
            )
        )
        journal_manager_role = core_models.Role.objects.get(
            slug="journal-manager",
        )
        self.api_client.post(
            path=url,
            data={
                "user": self.average_user.pk,
                "role": journal_manager_role.pk,
                "journal": self.journal.pk,
            },
            SERVER_NAME=self.journal.domain,
        )
        self.assertTrue(
            self.average_user.check_role(
                self.journal,
                journal_manager_role,
            )
        )

    @override_settings(URL_CONFIG="domain")
    def test_editor_cannot_assign_journal_manager_role(self):
        self.api_client.force_authenticate(user=self.editor)
        url = self.journal.site_url(
            reverse(
                "accountrole-list",
            )
        )
        journal_manager_role = core_models.Role.objects.get(
            slug="journal-manager",
        )
        self.api_client.post(
            path=url,
            data={
                "user": self.average_user.pk,
                "role": journal_manager_role.pk,
                "journal": self.journal.pk,
            },
            SERVER_NAME=self.journal.domain,
        )
        self.assertFalse(
            self.average_user.check_role(
                self.journal,
                journal_manager_role,
            )
        )

    @override_settings(URL_CONFIG="domain")
    def test_api_cannot_assign_reviewer_role(self):
        self.api_client.force_authenticate(
            user=self.staff_member,
        )

        url = self.journal.site_url(
            reverse(
                "accountrole-list",
            )
        )

        reviewer_role = core_models.Role.objects.get(
            slug="reviewer",
        )

        response = self.api_client.post(
            path=url,
            data={
                "user": self.average_user.pk,
                "role": reviewer_role.pk,
                "journal": self.journal.pk,
            },
            SERVER_NAME=self.journal.domain,
        )

        self.assertEqual(
            response.status_code,
            400,
        )

        self.assertFalse(
            core_models.AccountRole.objects.filter(
                user=self.average_user,
                journal=self.journal,
                role=reviewer_role,
            ).exists()
        )
