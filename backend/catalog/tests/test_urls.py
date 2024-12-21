import http

import django.test
import django.urls
import rest_framework.test

import users.models


class StaticURLTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(username="testuser")

    def setUp(self):
        self.guest_client = rest_framework.test.APIClient()
        self.authorized_client = rest_framework.test.APIClient()
        self.authorized_client.force_authenticate(user=self.user)

    def test_urls_exists_at_desired_location(self):
        urls = [
            django.urls.reverse("api:catalog:garments"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(
                    response.status_code,
                    http.HTTPStatus.OK,
                    f"Страница {url} не найдена",
                )

    def test_urls_method_not_allowed(self):
        urls = [
            django.urls.reverse("api:catalog:constructor-product-create"),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(
                    response.status_code,
                    http.HTTPStatus.METHOD_NOT_ALLOWED,
                    f"Страница {url} разрешает метод GET",
                )
