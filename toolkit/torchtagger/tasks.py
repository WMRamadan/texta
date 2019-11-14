from celery.decorators import task
import json

from toolkit.core.task.models import Task
from toolkit.torchtagger.models import TorchTagger as TorchTaggerObject
from toolkit.tools.show_progress import ShowProgress
from toolkit.base_task import BaseTask
from toolkit.tagger.data_sample import DataSample
from toolkit.torchtagger.torchtagger import TorchTagger
from toolkit.embedding.views import global_w2v_cache


@task(name="torchtagger_train_handler", base=BaseTask)
def torchtagger_train_handler(tagger_id, testing=False):
    try:
        # retrieve neurotagger & task objects
        tagger_object = TorchTaggerObject.objects.get(pk=tagger_id)
        task_object = tagger_object.task
        embedding_model = global_w2v_cache.get_model(tagger_object.embedding)

        show_progress = ShowProgress(task_object, multiplier=1)
        # create Datasample object for retrieving positive and negative sample
        data_sample = DataSample(tagger_object, show_progress=show_progress, join_fields=True)
        show_progress.update_step('training tagger')
        show_progress.update_view(0.0)
        # create TorchTagger
        tagger = TorchTagger(
            embedding_model, 
            model_arch=tagger_object.model_architecture, 
            num_epochs=int(tagger_object.num_epochs)
        )
        # train tagger and get result statistics
        tagger_stats = tagger.train(data_sample)
        # stats to model object
        tagger_object.f1_score = tagger_stats.f1_score
        tagger_object.precision = tagger_stats.precision
        tagger_object.recall = tagger_stats.recall
        tagger_object.accuracy = tagger_stats.accuracy
        tagger_object.training_loss = tagger_stats.training_loss
        # save tagger object
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
