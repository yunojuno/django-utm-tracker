# Generated by Django 3.0.7 on 2021-01-26 15:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("utm_tracker", "0003_increase_medium_chars"),
    ]

    operations = [
        migrations.AddField(
            model_name="leadsource",
            name="gclid",
            field=models.CharField(
                blank=True,
                help_text="Identifies a google click, is used for ad tracking in Google Analytics via Google Ads",
                max_length=255,
            ),
        ),
    ]
