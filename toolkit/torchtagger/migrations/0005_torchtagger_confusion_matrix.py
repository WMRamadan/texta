# Generated by Django 2.2.17 on 2021-02-02 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('torchtagger', '0004_remove_torchtagger_text_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='torchtagger',
            name='confusion_matrix',
            field=models.TextField(blank=True, default='[]', null=True),
        ),
    ]