# Generated by Django 2.2.28 on 2022-08-05 14:34

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def transfer_tagger_tasks(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Tagger = apps.get_model('tagger', 'Tagger')
    for orm in Tagger.objects.filter(task__isnull=False):
        task = getattr(orm, "task", None)
        if task:
            orm.tasks.add(orm.task)


def transfer_taggergroup_tasks(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    TaggerGroup = apps.get_model('tagger', 'TaggerGroup')
    for orm in TaggerGroup.objects.filter(task__isnull=False):
        task = getattr(orm, "task", None)
        if task:
            orm.tasks.add(orm.task)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0022_make_last_update_automatic'),
        ('tagger', '0031_auto_20220628_1601'),
    ]

    operations = [

        migrations.AddField(
            model_name='tagger',
            name='tasks',
            field=models.ManyToManyField(to='core.Task'),
        ),
        migrations.AddField(
            model_name='taggergroup',
            name='tasks',
            field=models.ManyToManyField(to='core.Task'),
        ),

        migrations.RunPython(transfer_taggergroup_tasks),
        migrations.RunPython(transfer_tagger_tasks),

        migrations.RemoveField(
            model_name='tagger',
            name='task',
        ),
        migrations.RemoveField(
            model_name='taggergroup',
            name='task',
        ),


        migrations.AlterField(
            model_name='tagger',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='tagger',
            name='description',
            field=models.CharField(help_text='Description of the task to distinguish it from others.', max_length=1000),
        ),
        migrations.AlterField(
            model_name='taggergroup',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='taggergroup',
            name='description',
            field=models.CharField(help_text='Description of the task to distinguish it from others.', max_length=1000),
        ),
    ]