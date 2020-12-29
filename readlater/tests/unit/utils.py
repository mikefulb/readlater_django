from django.contrib.auth.models import User


class TestUserMixin:

    TEST_USERNAME = 'TestUser'
    TEST_EMAIL = 'testuser@example.com'
    TEST_PASSWORD = 'testuserpassword'

    def setUp(self):
        self.user = User.objects.create_user('TestUser', 'testuser@example.com', 'testuserpassword')

    def tearDown(self):
        self.user.delete()

    def _login(self):
        self.client.force_login(user=self.user)
