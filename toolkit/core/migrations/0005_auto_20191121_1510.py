# Generated by Django 2.1.13 on 2019-11-21 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20191121_1406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='errors',
            field=models.TextField(default=''),
        ),
    ]
