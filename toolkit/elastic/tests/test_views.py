from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.test import APIClient
from toolkit.core.user_profile.models import UserProfile
from toolkit.tools.utils_for_tests import create_test_user, print_output

class ElasticViewsTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Owner of the project
        cls.user = create_test_user('user', 'my@email.com', 'pw')


    def setUp(self):
        self.client.login(username='user', password='pw')


    def test_get_indices(self):
        '''Tests if get_indices endpoint produces list of indices.'''
        response = self.client.get('/get_indices')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print_output('test_get_indices:response.data', response.data)
        self.assertTrue(isinstance(response.data, list))
        self.assertTrue(len(response.data) > 0)