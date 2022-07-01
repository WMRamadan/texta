# Generated by Django 2.2.28 on 2022-06-28 13:01

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tagger', '0030_tagger_classes'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagger',
            name='favorited_users',
            field=models.ManyToManyField(related_name='tagger_tagger_favorited_user', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='taggergroup',
            name='favorited_users',
            field=models.ManyToManyField(related_name='tagger_taggergroup_favorited_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
