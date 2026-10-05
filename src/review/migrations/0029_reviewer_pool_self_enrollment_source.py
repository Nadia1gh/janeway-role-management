from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("review", "0028_backfill_legacy_reviewers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="reviewerpoolmembership",
            name="source",
            field=models.CharField(
                choices=[
                    ("author", "Author"),
                    ("manual", "Manual"),
                    ("self_enrollment", "Self Enrollment"),
                    ("previous_reviewer", "Previous Reviewer"),
                    ("import", "Import"),
                    ("editorial_board", "Editorial Board"),
                    ("external", "External"),
                ],
                default="manual",
                max_length=30,
            ),
        ),
    ]
