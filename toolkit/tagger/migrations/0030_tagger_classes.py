# Generated by Django 2.2.28 on 2022-05-20 11:25

from django.db import migrations, models
import json


def convert_num_examples_to_classes(apps, schema_editor):
    Tagger = apps.get_model("tagger", "Tagger")
    for tagger in Tagger.objects.all():
        classes = list(json.loads(tagger.num_examples).keys())
        tagger.classes = json.dumps(classes, ensure_ascii=False)
        tagger.save()

class Migration(migrations.Migration):

    dependencies = [
        ('tagger', '0029_taggergroup_blacklisted_facts'),
    ]

    operations = [
        migrations.AddField(
            model_name='tagger',
            name='classes',
            field=models.TextField(default='[]'),
        ),
        migrations.RunPython(convert_num_examples_to_classes)
    ]