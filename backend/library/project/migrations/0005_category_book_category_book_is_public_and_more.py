# Generated by Django 5.1.1 on 2024-11-04 19:40

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0004_remove_book_cover_image_url_book_image"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name="book",
            name="category",
            field=models.CharField(
                choices=[
                    ("Novel", "Novel"),
                    ("Entertainment", "Entertainment"),
                    ("Education", "Education"),
                    ("Science", "Science"),
                    ("Biography", "Biography"),
                    ("History", "History"),
                    ("Fantasy", "Fantasy"),
                    ("Mystery", "Mystery"),
                    ("Romance", "Romance"),
                ],
                default="Novel",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="book",
            name="is_public",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="book",
            name="uploaded_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="uploaded_books",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="book",
            name="uploaded_on",
            field=models.DateTimeField(
                auto_now_add=True, default="2024-01-01 00:00:00"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="book",
            name="ebook",
            field=models.FileField(blank=True, null=True, upload_to="ebooks/"),
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
