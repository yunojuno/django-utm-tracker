# Generated by Django 3.2.6 on 2021-08-09 17:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tests", "0002_auto_20210126_0955"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="first_name",
            field=models.CharField(
                blank=True, max_length=150, verbose_name="first name"
            ),
        ),
    ]
