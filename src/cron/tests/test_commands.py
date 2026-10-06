from unittest.mock import patch

from django.test import TestCase
from django.core.management import call_command
from utils.testing import helpers
from cron.management.commands import send_reminders
from cron import forms, models
from review import models as review_models
from django.utils import timezone


class SendRemindersCommandTests(TestCase):
    """
    Unit tests for commands.
    """

    @classmethod
    def setUpTestData(cls):
        cls.press = helpers.create_press()
        cls.journal_one, cls.journal_two = helpers.create_journals()
        cls.review_assignment = helpers.create_review_assignment(
            journal=cls.journal_one
        )
        cls.review_reminder = helpers.create_reminder(
            journal=cls.journal_one, reminder_type="review"
        )

    def test_handle(self):
        call_command("send_reminders")
        reminder_item = self.review_reminder.items_for_reminder()[0]
        sent_check = models.SentReminder.objects.filter(
            type=self.review_reminder.type,
            object_id=reminder_item.pk,
            sent=timezone.now().date(),
        )
        self.assertTrue(sent_check)

class SendDigestEmailsCommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.press = helpers.create_press()
        cls.journal_one, cls.journal_two = helpers.create_journals()

        cls.pool_reviewer = helpers.create_user(
            "pool-digest@example.com",
            journal=cls.journal_one,
            enable_digest=True,
        )
        review_models.ReviewerPoolMembership.objects.create(
            account=cls.pool_reviewer,
            journal=cls.journal_one,
            status=review_models.ReviewerPoolMembership.STATUS_ACTIVE,
            source=review_models.ReviewerPoolMembership.SOURCE_MANUAL,
            is_available=True,
        )

        cls.legacy_reviewer = helpers.create_user(
            "legacy-digest@example.com",
            roles=["reviewer"],
            journal=cls.journal_one,
            enable_digest=True,
        )

        cls.blocked_legacy_reviewer = helpers.create_user(
            "blocked-digest@example.com",
            roles=["reviewer"],
            journal=cls.journal_one,
            enable_digest=True,
        )
        review_models.ReviewerPoolMembership.objects.create(
            account=cls.blocked_legacy_reviewer,
            journal=cls.journal_one,
            status=review_models.ReviewerPoolMembership.STATUS_BLOCKED,
            source=review_models.ReviewerPoolMembership.SOURCE_MANUAL,
            is_available=False,
        )

    @patch(
        "cron.management.commands.send_digest_emails.logic.process_reviewer_digest",
        return_value="",
    )
    @patch(
        "cron.management.commands.send_digest_emails.logic.process_digest_items",
        return_value="",
    )
    def test_pool_reviewers_are_processed_with_legacy_fallback(
        self,
        process_digest_items,
        process_reviewer_digest,
    ):
        call_command("send_digest_emails")

        process_reviewer_digest.assert_any_call(
            self.journal_one,
            self.pool_reviewer,
        )

        legacy_role = self.legacy_reviewer.accountrole_set.get(
            journal=self.journal_one,
            role__slug="reviewer",
        )
        process_digest_items.assert_any_call(
            self.journal_one,
            legacy_role,
        )

        blocked_calls = [
            call
            for call in process_reviewer_digest.call_args_list
            if call.args == (
                self.journal_one,
                self.blocked_legacy_reviewer,
            )
        ]
        self.assertEqual(blocked_calls, [])

        blocked_role = self.blocked_legacy_reviewer.accountrole_set.get(
            journal=self.journal_one,
            role__slug="reviewer",
        )
        self.assertNotIn(
            (
                (self.journal_one, blocked_role),
                {},
            ),
            [
                (call.args, call.kwargs)
                for call in process_digest_items.call_args_list
            ],
        )

    @patch("cron.logic.render_template.get_requestless_content")
    def test_reviewer_digest_is_scoped_to_journal(self, get_content):
        reviewer = helpers.create_user(
            "journal-scoped-digest@example.com",
            journal=self.journal_one,
        )

        assignment_one = helpers.create_review_assignment(
            journal=self.journal_one,
            reviewer=reviewer,
        )
        helpers.create_review_assignment(
            journal=self.journal_two,
            reviewer=reviewer,
        )

        from cron import logic

        logic.process_reviewer_digest(
            self.journal_one,
            reviewer,
        )

        context = get_content.call_args.args[0]

        self.assertEqual(
            list(context["pending_requests"]),
            [assignment_one],
        )
        self.assertEqual(
            list(context["overdue_requests"]),
            [],
        )
