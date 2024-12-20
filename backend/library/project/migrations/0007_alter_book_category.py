# Generated by Django 5.1.1 on 2024-11-09 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("project", "0006_alter_book_isbn"),
    ]

    operations = [
        migrations.AlterField(
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
                max_length=50,
            ),
        ),
    ]
