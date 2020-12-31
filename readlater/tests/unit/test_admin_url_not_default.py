import logging

from .utils import TestUserMixin

logger = logging.getLogger(__name__)
logging.disable(logging.NOTSET)
logger.setLevel(logging.DEBUG)

from django.test import TestCase


class AdminUrlNotDefaultTest(TestCase):

    def test_admin_url_not_default(self):
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/admin')
        self.assertEqual(response.status_code, 404)
