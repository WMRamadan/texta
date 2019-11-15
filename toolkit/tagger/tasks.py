import os
import json
import secrets

from celery.decorators import task

from toolkit.core.task.models import Task
from toolkit.tagger.models import Tagger, TaggerGroup
from toolkit.settings import NUM_WORKERS, MODELS_DIR
from toolkit.embedding.phraser import Phraser
from toolkit.elastic.searcher import ElasticSearcher
from toolkit.tools.show_progress import ShowProgress
from toolkit.tagger.text_tagger import TextTagger
from toolkit.tools.text_processor import TextProcessor
from toolkit.tagger.plots import create_tagger_plot
from toolkit.base_task import BaseTask
from toolkit.tools.mlp_analyzer import MLPAnalyzer
from toolkit.elastic.feedback import Feedback
from toolkit.elastic.data_sample import DataSample


def create_tagger_batch(tagger_group_id, taggers_to_create):
    '''Creates Tagger objects from list of tagger data and saves into tagger group object.'''
    # retrieve Tagger Group object
    tagger_group_object = TaggerGroup.objects.get(pk=tagger_group_id)
    # iterate through batch
    for tagger_data in taggers_to_create:
        created_tagger = Tagger.objects.create(**tagger_data,
        author=tagger_group_object.author,
        project=tagger_group_object.project)
        # add and save
        tagger_group_object.taggers.add(created_tagger)
        tagger_group_object.save()


@task(name="create_tagger_objects", base=BaseTask)
def create_tagger_objects(tagger_group_id, tagger_serializer, tags, tag_queries, batch_size=100):
    '''Task for creating Tagger objects inside Tagger Group to prevent database timeouts.'''
    # create tagger objects
    taggers_to_create = []
    for i,tag in enumerate(tags):
        tagger_data = tagger_serializer.copy()
        tagger_data.update({'query': json.dumps(tag_queries[i])})
        tagger_data.update({'description': tag})
        tagger_data.update({'fields': json.dumps(tagger_data['fields'])})
        taggers_to_create.append(tagger_data)
        # if batch size reached, save result
        if len(taggers_to_create) >= batch_size:
            create_tagger_batch(tagger_group_id, taggers_to_create)
            taggers_to_create = []
    # if any taggers remaining
    if taggers_to_create:
        # create tagger objects of remaining items
        create_tagger_batch(tagger_group_id, taggers_to_create)
    return True


@task(name="train_tagger", base=BaseTask)
def train_tagger(tagger_id):
    '''Task for training Text Tagger.'''
    # retrieve tagger & task objects
    tagger_object = Tagger.objects.get(pk=tagger_id)
    task_object = tagger_object.task
    # create progress object
    show_progress = ShowProgress(task_object, multiplier=1)
    show_progress.update_step('scrolling positives')
    show_progress.update_view(0)
    
    try:
        # retrieve indices & field data from project 
        indices = tagger_object.project.indices
        field_data = json.loads(tagger_object.fields)
        stop_words = tagger_object.stop_words.split(' ')

        # load embedding and create text processor
        if tagger_object.embedding:
            phraser = Phraser(embedding_id=tagger_object.embedding.pk)
            phraser.load()
            text_processor = TextProcessor(phraser=phraser, remove_stop_words=True, custom_stop_words=stop_words)
        else:
            text_processor = TextProcessor(remove_stop_words=True, custom_stop_words=stop_words)
        # create Datasample object for retrieving positive and negative sample
        data_sample = DataSample(
            tagger_object,
            show_progress=show_progress, 
            text_processor=text_processor
        )
        # update status to training
        show_progress.update_step('training')
        show_progress.update_view(0)
        # train model
        tagger = TextTagger(tagger_id)
        tagger.train(
            data_sample,
            field_list=json.loads(tagger_object.fields),
            classifier=tagger_object.classifier,
            vectorizer=tagger_object.vectorizer
        )
        # update status to saving
        show_progress.update_step('saving')
        show_progress.update_view(0)
        # save tagger to disk
        tagger_path = os.path.join(MODELS_DIR, 'tagger', f'tagger_{tagger_id}_{secrets.token_hex(10)}')
        tagger.save(tagger_path)
        # save model locations
        tagger_object.location = json.dumps({'tagger': tagger_path})
        tagger_object.precision = float(tagger.statistics['precision'])
        tagger_object.recall = float(tagger.statistics['recall'])
        tagger_object.f1_score = float(tagger.statistics['f1_score'])
        tagger_object.num_features = tagger.statistics['num_features']
        tagger_object.plot.save(f'{secrets.token_hex(15)}.png', create_tagger_plot(tagger.statistics))
        tagger_object.save()
        # declare the job done
        show_progress.update_step('')
        show_progress.update_view(100.0)
        task_object.update_status(Task.STATUS_COMPLETED, set_time_completed=True)
        return True

    except Exception as e:
        # declare the job failed
        show_progress.update_errors(e)
        task_object.update_status(Task.STATUS_FAILED)
        raise


@task(name="apply_tagger", base=BaseTask)
def apply_tagger(text, tagger_id, input_type, lemmatize=False):
    '''Task for applying tagger to text.'''
    from toolkit.tagger.tagger_views import global_tagger_cache
    from toolkit.embedding.views import global_phraser_cache
    # get tagger object
    tagger = Tagger.objects.get(pk=tagger_id)
    # get lemmatizer if needed
    lemmatizer = None
    if lemmatize:
        lemmatizer = MLPAnalyzer()
    # create text processor object for tagger
    stop_words = tagger.stop_words.split(' ')
    if tagger.embedding:
        phraser = global_phraser_cache.get_model(tagger.embedding)
        text_processor = TextProcessor(phraser=phraser, remove_stop_words=True, custom_stop_words=stop_words, lemmatizer=lemmatizer)
    else:
        text_processor = TextProcessor(remove_stop_words=True, custom_stop_words=stop_words, lemmatizer=lemmatizer)
    # load tagger
    tagger = global_tagger_cache.get_model(tagger)
    if not tagger:
        return None
    # check input type
    if input_type == 'doc':
        tagger_result = tagger.tag_doc(text)
    else:
        tagger_result = tagger.tag_text(text)
    # check if prediction positive
    decision = bool(tagger_result[0])
    if not decision:
        return None
    # return tag info
    return {'tag': tagger.description, 'probability': tagger_result[1], 'tagger_id': tagger_id}
