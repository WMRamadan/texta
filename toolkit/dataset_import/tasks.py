from celery.decorators import task

from .dataset import Dataset
from .models import DatasetImport
from toolkit.core.task.models import Task
from toolkit.tools.show_progress import ShowProgress
from toolkit.base_task import BaseTask


@task(name="import_dataset", base=BaseTask)
def import_dataset(dataset_import_id):
    # retrieve object & task
    import_object = DatasetImport.objects.get(pk=dataset_import_id)
    task_object = import_object.task
    # create progress
    show_progress = ShowProgress(task_object, multiplier=1)
    show_progress.update_step('importing dataset')
    show_progress.update_view(0)
    try:
        # retrieve file path from object
        file_path = import_object.file.path
        ds = Dataset(file_path, import_object.index, show_progress=show_progress, separator=import_object.separator)
        errors = ds.import_dataset()
        # update errors
        if errors:
            show_progress.update_errors(errors)
        # update num_documents
        import_object.num_documents = ds.num_records
        import_object.num_documents_success = ds.num_records_success
        import_object.save()
        # add imported index to project indices
        project_obj = import_object.project
        project_obj.indices.append(import_object.index)
        project_obj.save(add_indices=project_obj.indices)
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
