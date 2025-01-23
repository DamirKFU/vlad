import http

import django.test
import django.urls
import rest_framework.test

import catalog.models
import users.models


class StaticURLTests(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = users.models.User.objects.create_user(username="testuser")
        cls.product = catalog.models.Product.objects.create(
            name="Test Product",
            price=100,
        )
        cls.guest_client = rest_framework.test.APIClient()
        cls.authorized_client = rest_framework.test.APIClient()
        cls.authorized_client.force_authenticate(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    def test_garments_url(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:garments")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_garments_url_authorized(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:garments")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_products_url(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:products")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_products_url_authorized(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:products")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_product_detail_url(self):
        response = self.guest_client.get(
            django.urls.reverse(
                "api:catalog:product-detail",
                kwargs={"pk": self.product.id},
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_product_detail_url_authorized(self):
        response = self.authorized_client.get(
            django.urls.reverse(
                "api:catalog:product-detail",
                kwargs={"pk": self.product.id},
            )
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_cart_url(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_cart_url_not_authorized(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:cart")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_order_url(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.OK)

    def test_order_url_not_authorized(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:order-history")
        )
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)

    def test_order_detail_url(self):
        response = self.authorized_client.get(
            django.urls.reverse("api:catalog:order-detail", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, http.HTTPStatus.NOT_FOUND)

    def test_order_detail_url_not_authorized(self):
        response = self.guest_client.get(
            django.urls.reverse("api:catalog:order-detail", kwargs={"pk": 1})
        )
        self.assertEqual(response.status_code, http.HTTPStatus.UNAUTHORIZED)
