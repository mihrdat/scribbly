# Generated by Django 4.1.2 on 2024-04-06 12:00

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0004_remove_default_value_for_name"),
    ]

    operations = [
        migrations.RenameField(
            model_name="message",
            old_name="user",
            new_name="sender",
        ),
    ]
