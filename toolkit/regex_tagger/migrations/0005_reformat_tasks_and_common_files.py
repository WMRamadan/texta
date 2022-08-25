# Generated by Django 2.2.28 on 2022-08-08 13:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def transfer_regex_tagger_tasks(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    RegexTagger = apps.get_model('regex_tagger', 'RegexTagger')
    for orm in RegexTagger.objects.filter(task__isnull=False):
        task = getattr(orm, "task", None)
        if task:
            orm.tasks.add(orm.task)



def transfer_regex_tagger_group_tasks(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    RegexTaggerGroup = apps.get_model('regex_tagger', 'RegexTaggerGroup')
    for orm in RegexTaggerGroup.objects.filter(task__isnull=False):
        task = getattr(orm, "task", None)
        if task:
            orm.tasks.add(orm.task)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0022_make_last_update_automatic'),
        ('regex_tagger', '0004_auto_20220628_1601'),
    ]

    operations = [
        migrations.AddField(
            model_name='regextagger',
            name='tasks',
            field=models.ManyToManyField(to='core.Task'),
        ),
        migrations.AddField(
            model_name='regextaggergroup',
            name='tasks',
            field=models.ManyToManyField(to='core.Task'),
        ),

        migrations.RunPython(transfer_regex_tagger_tasks),
        migrations.RunPython(transfer_regex_tagger_group_tasks),

        migrations.RemoveField(
            model_name='regextagger',
            name='task',
        ),
        migrations.RemoveField(
            model_name='regextaggergroup',
            name='task',
        ),

        migrations.AlterField(
            model_name='regextagger',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='regextagger',
            name='description',
            field=models.CharField(help_text='Description of the task to distinguish it from others.', max_length=1000),
        ),
        migrations.AlterField(
            model_name='regextaggergroup',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='regextaggergroup',
            name='description',
            field=models.CharField(help_text='Description of the task to distinguish it from others.', max_length=1000),
        ),
    ]