# Generated by Django 4.1.2 on 2023-10-28 13:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0012_add_field_comments_count_to_article"),
    ]

    operations = [
        migrations.RenameField(
            model_name="comment",
            old_name="reply_to",
            new_name="parent",
        ),
    ]
