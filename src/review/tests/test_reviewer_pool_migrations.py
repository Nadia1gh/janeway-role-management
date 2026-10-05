import importlib

from django.apps import apps as django_apps
from django.test import TestCase

from review.models import ReviewerPoolMembership
from utils.testing import helpers


migration = importlib.import_module(
    "review.migrations.0028_backfill_legacy_reviewers"
)


class TestReviewerPoolLegacyBackfill(TestCase):

    def setUp(self):
        self.journal, _ = helpers.create_journals()

        helpers.create_roles(
            [
                "Reviewer",
            ]
        )

        self.account = helpers.create_user(
            "legacy-reviewer@example.com",
            [
                "reviewer",
            ],
            self.journal,
        )

    def run_backfill(self):
        migration.backfill_legacy_reviewers(
            django_apps,
            None,
        )

    def test_legacy_reviewer_is_added_to_pool(self):
        self.assertFalse(
            ReviewerPoolMembership.objects.filter(
                account=self.account,
                journal=self.journal,
            ).exists()
        )

        self.run_backfill()

        membership = ReviewerPoolMembership.objects.get(
            account=self.account,
            journal=self.journal,
        )

        self.assertEqual(
            membership.status,
            ReviewerPoolMembership.STATUS_ACTIVE,
        )

        self.assertEqual(
            membership.source,
            ReviewerPoolMembership.SOURCE_PREVIOUS_REVIEWER,
        )

        self.assertTrue(
            membership.is_available,
        )

    def test_blocked_membership_is_preserved(self):
        membership = ReviewerPoolMembership.objects.create(
            account=self.account,
            journal=self.journal,
            status=ReviewerPoolMembership.STATUS_BLOCKED,
            source=ReviewerPoolMembership.SOURCE_MANUAL,
            is_available=False,
        )

        self.run_backfill()

        membership.refresh_from_db()

        self.assertEqual(
            membership.status,
            ReviewerPoolMembership.STATUS_BLOCKED,
        )

        self.assertEqual(
            membership.source,
            ReviewerPoolMembership.SOURCE_MANUAL,
        )

        self.assertFalse(
            membership.is_available,
        )

    def test_author_candidate_legacy_reviewer_is_promoted(self):
        membership = ReviewerPoolMembership.objects.create(
            account=self.account,
            journal=self.journal,
            status=ReviewerPoolMembership.STATUS_CANDIDATE,
            source=ReviewerPoolMembership.SOURCE_AUTHOR,
            is_available=False,
        )

        self.run_backfill()

        membership.refresh_from_db()

        self.assertEqual(
            membership.status,
            ReviewerPoolMembership.STATUS_ACTIVE,
        )

        self.assertEqual(
            membership.source,
            ReviewerPoolMembership.SOURCE_PREVIOUS_REVIEWER,
        )

        # Existing availability preference is preserved.
        self.assertFalse(
            membership.is_available,
        )

    def test_inactive_membership_is_preserved(self):
        membership = ReviewerPoolMembership.objects.create(
            account=self.account,
            journal=self.journal,
            status=ReviewerPoolMembership.STATUS_INACTIVE,
            source=ReviewerPoolMembership.SOURCE_MANUAL,
            is_available=False,
        )

        self.run_backfill()

        membership.refresh_from_db()

        self.assertEqual(
            membership.status,
            ReviewerPoolMembership.STATUS_INACTIVE,
        )

        self.assertEqual(
            membership.source,
            ReviewerPoolMembership.SOURCE_MANUAL,
        )

        self.assertFalse(
            membership.is_available,
        )