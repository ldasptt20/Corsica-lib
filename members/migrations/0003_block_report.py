from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("members", "0002_message_favorite"),
    ]

    operations = [
        migrations.CreateModel(
            name="Block",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocked_profiles", to="members.profile")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="blocked_by", to="members.profile")),
            ],
        ),
        migrations.AddConstraint(
            model_name="block",
            constraint=models.UniqueConstraint(fields=("owner", "target"), name="unique_block"),
        ),
        migrations.CreateModel(
            name="Report",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reason", models.CharField(max_length=500)),
                ("created", models.DateTimeField(auto_now_add=True)),
                ("reviewed", models.BooleanField(default=False)),
                ("reporter", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submitted_reports", to="members.profile")),
                ("target", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="received_reports", to="members.profile")),
            ],
        ),
    ]
