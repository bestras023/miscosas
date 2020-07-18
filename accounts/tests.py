from django.test import TestCase
from rest_framework.test import APIClient
import json


class UserTest(TestCase):

    def test_retrieve(self):
        client = APIClient()
        response = client.get('/api/accounts/retrieve')
        assert response.status_code == 301

    def test_register(self):
        client = APIClient()
        credentials = {
            "user": {
                "username": "bestras",
                "password": "123456"
            }
        }
        response = client.post('/api/accounts/register/', credentials, format='json')
        assert response.status_code == 201
        content = response.content.decode('utf8')
        content = json.loads(content)
        assert content['user']['username'] == credentials['user']['username']

