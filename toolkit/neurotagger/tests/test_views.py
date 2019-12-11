import json
import os
from io import BytesIO

from rest_framework import status
from rest_framework.test import APITestCase

from toolkit.core.project.models import Project
from toolkit.core.task.models import Task
from toolkit.neurotagger import choices
from toolkit.neurotagger.models import Neurotagger
from toolkit.test_settings import TEST_FACT_NAME, TEST_FIELD, TEST_FIELD_CHOICE, TEST_INDEX
from toolkit.tools.utils_for_tests import create_test_user, print_output


class NeurotaggerViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Owner of the project
        cls.user = create_test_user('neurotaggerOwner', 'my@email.com', 'pw')
        # cls.user.is_superuser = True
        # cls.user.save()
        cls.project = Project.objects.create(
            title='neurotaggerTestProject',
            indices=TEST_INDEX
        )
        cls.project.users.add(cls.user)
        cls.url = f'/projects/{cls.project.id}/neurotaggers/'
        cls.project_url = f'/projects/{cls.project.id}'


    def setUp(self):
        self.client.login(username='neurotaggerOwner', password='pw')


    def tearDown(self):
        Neurotagger.objects.all().delete()


    def test_run(self):
        self.run_create_and_tag_multilabel()
        # run these last ->
        self.create_neurotagger_with_empty_fields()
        self.create_neurotagger_then_delete_neurotagger_and_created_model()


    def run_create_and_tag_multilabel(self):
        """Tests the endpoint for a new multilabel Neurotagger with facts, and if a new Task gets created via the signal"""
        payload = {
            "description": "TestNeurotaggerView",
            "fact_name": TEST_FACT_NAME,
            "model_architecture": choices.model_arch_choices[0][0],
            "fields": TEST_FIELD_CHOICE,
            "maximum_sample_size": 500,
        }

        response = self.client.post(self.url, payload, format='json')
        print_output('test_create_neurotagger_training_and_task_signal:response.data', response.data)
        # Check if Neurotagger gets created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_neurotagger = Neurotagger.objects.get(id=response.data['id'])

        # Test the tagging endpoints
        self.run_tag_text(tagger_id=created_neurotagger.id)
        self.run_tag_doc(tagger_id=created_neurotagger.id)

        # Test model import
        imported_neurotagger = self.run_model_export_import(tagger_id=created_neurotagger.id)

        # Check if Task gets created via a signal
        self.assertTrue(created_neurotagger.task is not None)
        if created_neurotagger.task.errors:
            print_output('test_create_neurotagger_training_and_task_signal:task.errors', created_neurotagger.task.errors)

        # Check if Neurotagger gets trained and completed
        self.assertEqual(created_neurotagger.task.status, Task.STATUS_COMPLETED)


    def run_tag_text(self, tagger_id=None):
        """Tests the endpoint for the tag_text action"""
        payload = {"text": "This is some test text for the Tagger Test"}
        tag_text_url = f'{self.url}{tagger_id}/tag_text/'
        response = self.client.post(tag_text_url, payload)
        print_output('test_tag_text:response.data', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response data is not empty, but a result instead
        self.assertTrue(response.data)
        self.assertTrue('tags' in response.data)


    def run_tag_doc(self, tagger_id=None):
        """Tests the endpoint for the tag_doc action"""
        payload = {"doc": json.dumps({TEST_FIELD: "This is some test text for the Tagger Test"})}
        tag_text_url = f'{self.url}{tagger_id}/tag_doc/'
        response = self.client.post(tag_text_url, payload)
        print_output('test_tag_doc:response.data', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response data is not empty, but a result instead
        self.assertTrue(response.data)
        self.assertTrue('tags' in response.data)


    def run_model_export_import(self, tagger_id=None):
        """Tests endpoint for model export and import"""
        # retrieve model zip
        url = f'{self.url}{tagger_id}/export_model/'
        response = self.client.get(url)
        # post model zip
        import_url = f'{self.project_url}/import_model/'
        response = self.client.post(import_url, data={'file': BytesIO(response.content)})
        print_output('test_import_model:response.data', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Test tagging with imported model
        tagger_id = response.data['id']
        self.run_tag_text(tagger_id=tagger_id)
        # return obj location for removal
        return Neurotagger.objects.get(id=tagger_id)


    def run_patch_on_neurotagger_instances(self, tagger_id=None):
        """ Tests patch response success for Tagger fields """
        payload = {
            "description": "PatchedTestNeurotaggerView",
            "fact_name": TEST_FACT_NAME,
            "model_architecture": choices.model_arch_choices[0][0],
            "fields": TEST_FIELD_CHOICE,
            "maximum_sample_size": 500,
        }

        neurotagger_url = f'{self.url}{tagger_id}/'
        patch_response = self.client.patch(neurotagger_url, payload, format='json')
        print_output("patch_response", patch_response.data)
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)


    def run_put_on_neurotagger_instances(self, tagger_id=None):
        """ Tests put response success for Tagger fields """
        payload = {
            "description": "PutTestNeurotaggerView",
            "fact_name": TEST_FACT_NAME,
            "model_architecture": choices.model_arch_choices[0][0],
            "fields": TEST_FIELD_CHOICE,
            "maximum_sample_size": 500,
        }

        neurotagger_url = f'{self.url}{tagger_id}/'
        put_response = self.client.put(neurotagger_url, payload, format='json')
        print_output("put_response", put_response.data)
        self.assertEqual(put_response.status_code, status.HTTP_200_OK)


    def create_neurotagger_then_delete_neurotagger_and_created_model(self):
        payload = {
            "description": "TestNeurotaggerView",
            "fact_name": TEST_FACT_NAME,
            "model_architecture": choices.model_arch_choices[0][0],
            "fields": TEST_FIELD_CHOICE,
            "maximum_sample_size": 500,
        }
        create_response = self.client.post(self.url, payload, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        created_neurotagger = Neurotagger.objects.get(id=create_response.data['id'])
        created_neurotagger_id = create_response.data['id']
        created_neurotagger_url = f'{self.url}{created_neurotagger_id}/'

        neurotagger_model_location = created_neurotagger.model.path
        tokenizer_model_location = created_neurotagger.tokenizer_model.path
        tokenizer_vocab_model_location = created_neurotagger.tokenizer_vocab.path

        for path in (
                neurotagger_model_location,
                tokenizer_model_location,
                tokenizer_vocab_model_location,
                created_neurotagger.plot.path,
        ):
            self.assertEqual(os.path.isfile(path), True)

        # test PATCH/PUT before removal.
        # self.run_patch_on_neurotagger_instances(tagger_id=created_neurotagger.id)
        # self.run_put_on_neurotagger_instances(tagger_id=created_neurotagger.id)


        delete_response = self.client.delete(created_neurotagger_url, format='json')
        print_output('delete_response.data: ', delete_response.data)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        for path in (
                neurotagger_model_location,
                tokenizer_model_location,
                tokenizer_vocab_model_location,
                created_neurotagger.plot.path,
        ):
            self.assertEqual(os.path.isfile(path), False)


    def create_neurotagger_with_empty_fields(self):
        """ tests to_repr serializer constant. Should fail because empty fields obj is filtered out in view"""
        payload = {
            "description": "TestNeurotaggerView",
            "fact_name": TEST_FACT_NAME,
            "model_architecture": choices.model_arch_choices[0][0],
            "fields": [],
            "maximum_sample_size": 500,
        }
        create_response = self.client.post(self.url, payload, format='json')
        print_output("empty_fields_response", create_response.data)
        self.assertEqual(create_response.status_code, status.HTTP_400_BAD_REQUEST)
