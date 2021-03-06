from django.contrib.auth.models import User


def get_login_redirect_url(url):
    return f'/readlater/accounts/login/?next={url}'


class TestUserMixin:

    TEST_USERNAME = 'TestUser'
    TEST_EMAIL = 'testuser@example.com'
    TEST_PASSWORD = 'testuserpassword'

    def setUp(self):
        self.user = User.objects.create_user(self.TEST_USERNAME, self.TEST_EMAIL,
                                             self.TEST_PASSWORD)

    def tearDown(self):
        self.user.delete()

    def _login(self):
        self.client.force_login(user=self.user)


class AssertUnauthRedirectMixin:

    def assert_unauth_redirect_url(self, url, template=None):
        response = self.client.get(url)
        self.assertRedirects(response, f'/readlater/accounts/login/?next={url}')
        if template is not None:
            response = self.client.get(url, follow=True)
            self.assertTemplateUsed(response, template)

    def assert_unauth_redirect_post(self, url, data=None, template=None):
        response = self.client.post(url, data=data, follow=True)
        self.assertRedirects(response, f'/readlater/accounts/login/?next={url}')
        if template is not None:
            response = self.client.get(url, follow=True)
            self.assertTemplateUsed(response, template)
