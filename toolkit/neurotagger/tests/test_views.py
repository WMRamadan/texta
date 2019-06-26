import json
import os
from django.db.models import signals

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient

from toolkit.test_settings import TEST_FIELD, TEST_INDEX, TEST_FIELD_CHOICE
from toolkit.core.project.models import Project
from toolkit.neurotagger.models import Neurotagger
from toolkit.core.task.models import Task
from toolkit.utils.utils_for_tests import create_test_user, print_output, remove_file

class NeurotaggerViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Owner of the project
        cls.url = f'/neurotaggers/'
        cls.user = create_test_user('neurotaggerOwner', 'my@email.com', 'pw')

        cls.project = Project.objects.create(
            title='neurotaggerTestProject',
            owner=cls.user,
            indices=TEST_INDEX
        )

        cls.user.profile.activate_project(cls.project)

        cls.test_neurotagger = Neurotagger.objects.create(
            description='NeurotaggerForTesting',
            project=cls.project,
            author=cls.user,
            vectorizer=0,
            classifier=0,
            fields=TEST_FIELD_CHOICE,
            maximum_sample_size=500,
            negative_multiplier=1.0,
        )
        # Get the object, since .create does not update on changes
        cls.test_neurotagger = Neurotagger.objects.get(id=cls.test_neurotagger.id)


    def setUp(self):
        self.client.login(username='neurotaggerOwner', password='pw')


    def test_run(self):
        self.run_create_neurotagger_training_and_task_signal()


    def run_create_neurotagger_training_and_task_signal(self):
        '''Tests the endpoint for a new Neurotagger, and if a new Task gets created via the signal'''
        payload = {
            "description": "TestNeurotagger",
            "query": "",
            "fields": TEST_FIELD_CHOICE,
            "vectorizer": 0,
            "classifier": 0,
            "maximum_sample_size": 500,
            "negative_multiplier": 1.0,
        }

        response = self.client.post(self.url, payload)
        print_output('test_create_neurotagger_training_and_task_signal:response.data', response.data)
        # Check if Neurotagger gets created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_neurotagger = Neurotagger.objects.get(id=response.data['id'])
        # Remove neurotagger files after test is done
        self.addCleanup(remove_file, json.loads(created_neurotagger.location)['neurotagger'])
        self.addCleanup(remove_file, created_neurotagger.plot.path)
        # Check if Task gets created via a signal
        self.assertTrue(created_neurotagger.task is not None)
        # Check if Neurotagger gets trained and completed
        self.assertEqual(created_neurotagger.task.status, Task.STATUS_COMPLETED)


    @classmethod
    def tearDownClass(cls):
        # TODO
        pass
        # remove_file(json.loads(cls.test_neurotagger.location)['neurotagger'])
        # remove_file(cls.test_neurotagger.plot.path)