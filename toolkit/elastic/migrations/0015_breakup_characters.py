# Generated by Django 2.2.22 on 2021-08-24 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('elastic', '0014_auto_20210618_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='searchfieldstagger',
            name='breakup_character',
            field=models.TextField(default='\n'),
        ),
        migrations.AddField(
            model_name='searchfieldstagger',
            name='use_breakup',
            field=models.BooleanField(default=True),
        ),
    ]
