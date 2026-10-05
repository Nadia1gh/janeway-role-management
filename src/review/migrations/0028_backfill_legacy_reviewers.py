from django.db import migrations


def backfill_legacy_reviewers(apps, schema_editor):
    AccountRole = apps.get_model("core", "AccountRole")
    Role = apps.get_model("core", "Role")
    ReviewerPoolMembership = apps.get_model(
        "review",
        "ReviewerPoolMembership",
    )

    reviewer_role = Role.objects.filter(
        slug="reviewer",
    ).first()

    if not reviewer_role:
        return

    legacy_reviewers = (
        AccountRole.objects.filter(
            role_id=reviewer_role.pk,
        )
        .values_list(
            "user_id",
            "journal_id",
        )
        .iterator()
    )

    for account_id, journal_id in legacy_reviewers:
        membership, created = (
            ReviewerPoolMembership.objects.get_or_create(
                account_id=account_id,
                journal_id=journal_id,
                defaults={
                    "status": "active",
                    "source": "previous_reviewer",
                    "is_available": True,
                },
            )
        )

        if created:
            continue

        # Repair only memberships created by the old author-candidate path.
        # Existing ACTIVE, INACTIVE, BLOCKED, or other intentional states
        # remain authoritative.
        if (
            membership.status == "candidate"
            and membership.source == "author"
        ):
            membership.status = "active"
            membership.source = "previous_reviewer"
            membership.save(
                update_fields=[
                    "status",
                    "source",
                ]
            )


class Migration(migrations.Migration):

    dependencies = [
        (
            "review",
            "0027_reviewerpoolmembership_and_more",
        ),
        (
            "core",
            "0111_merge_20260603_2206",
        ),
    ]

    operations = [
        migrations.RunPython(
            backfill_legacy_reviewers,
            migrations.RunPython.noop,
        ),
    ]