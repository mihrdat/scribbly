# Generated by Django 4.1.2 on 2023-10-23 12:35

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0004_create_articleimage"),
    ]

    operations = [
        migrations.RenameField(
            model_name="articleimage",
            old_name="url",
            new_name="image",
        ),
    ]