# Generated by Django 2.1.15 on 2020-05-11 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('elastic', '0003_index'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0012_project_author'),
        ('mlp', '0003_remove_mlpprocessor_indices'),
    ]

    operations = [
        migrations.CreateModel(
            name='MLPWorker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=1000)),
                ('query', models.TextField(default='{"query": {"match_all": {}}}')),
                ('fields', models.TextField(default='[]')),
                ('analyzers', models.TextField(default='[]')),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('indices', models.ManyToManyField(to='elastic.Index')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Project')),
                ('task', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Task')),
            ],
        ),
        migrations.RemoveField(
            model_name='mlpprocessor',
            name='author',
        ),
        migrations.RemoveField(
            model_name='mlpprocessor',
            name='project',
        ),
        migrations.RemoveField(
            model_name='mlpprocessor',
            name='task',
        ),
        migrations.DeleteModel(
            name='MLPProcessor',
        ),
    ]