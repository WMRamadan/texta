# Generated by Django 2.1.13 on 2019-11-26 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tagger', '0005_auto_20191125_0935'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagger',
            name='model_size',
            field=models.FloatField(default=None, null=True),
        ),
    ]