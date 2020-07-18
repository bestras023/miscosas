from django.test import TestCase
from rest_framework.test import APIClient
import json


class FeederTest(TestCase):

    def test_retrieve(self):
        client = APIClient()
        response = client.get('/api/home/retrieve')
        assert response.status_code == 301

    def test_create(self):
        client = APIClient()
        info = {
            "feeder": "Youtube",
            "url": "UC300utwSVAYOoRLEqmsprfg"
        }
        response = client.post('/api/home/create/', info)
        content = response.content.decode('utf8')
        content = json.loads(content)
        assert content == 200
