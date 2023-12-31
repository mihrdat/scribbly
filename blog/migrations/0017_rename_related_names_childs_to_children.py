# Generated by Django 4.1.2 on 2023-12-30 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("blog", "0016_rename_field_reply_to_author_on_comment_to_reply_to"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="parent",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="children",
                to="blog.category",
            ),
        ),
    ]
