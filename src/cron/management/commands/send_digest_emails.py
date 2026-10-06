from django.core.management.base import BaseCommand

from core import models
from cron import logic
from journal import models as journal_models
from review import models as review_models


class Command(BaseCommand):
    """
    A management command that sends digest emails.
    """

    help = "Sends digest emails"

    def handle(self, *args, **options):
        journals = journal_models.Journal.objects.all()

        for journal in journals:
            print("Processing journal {0} - {1}".format(journal.pk, journal.code))

            users = models.Account.objects.filter(enable_digest=True)

            for user in users:
                print("Processing user {0}".format(user.full_name()))

                # Reviewer membership is now managed by ReviewerPoolMembership.
                # Exclude the legacy reviewer role here so a migrated reviewer
                # cannot receive the reviewer digest twice.
                user_roles = (
                    models.AccountRole.objects.filter(
                        user=user,
                        journal=journal,
                    )
                    .exclude(role__slug="reviewer")
                    .select_related("role")
                )

                text = ""
                for user_role in user_roles:
                    print("Processing role {0}".format(user_role.role.name))

                    items = logic.process_digest_items(journal, user_role)
                    if items:
                        text = text + "\n\n" + items

                membership = (
                    review_models.ReviewerPoolMembership.objects.filter(
                        account=user,
                        journal=journal,
                    ).first()
                )

                reviewer_items = None

                if membership:
                    # Pool status is authoritative whenever a membership exists.
                    if (
                        membership.status
                        == review_models.ReviewerPoolMembership.STATUS_ACTIVE
                    ):
                        print("Processing reviewer pool membership")
                        reviewer_items = logic.process_reviewer_digest(
                            journal,
                            user,
                        )
                else:
                    # Backward-compatible fallback for reviewer roles that have
                    # not yet been represented in ReviewerPoolMembership.
                    legacy_reviewer_role = (
                        models.AccountRole.objects.filter(
                            user=user,
                            journal=journal,
                            role__slug="reviewer",
                        )
                        .select_related("role")
                        .first()
                    )

                    if legacy_reviewer_role:
                        print(
                            "Processing role {0}".format(
                                legacy_reviewer_role.role.name
                            )
                        )
                        reviewer_items = logic.process_digest_items(
                            journal,
                            legacy_reviewer_role,
                        )

                if reviewer_items:
                    text = text + "\n\n" + reviewer_items

                print(text)
                print("-------------------------------------------")
