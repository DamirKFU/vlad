import json

import django.test
import django.urls
import rest_framework.status as status

import catalog.models
import staff.models
import users.models


class StaffOrderListViewTest(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

        self.user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.designer_role = users.models.UserRole.objects.create(
            role=users.models.Role.DESIGNER
        )
        self.moderator_role = users.models.UserRole.objects.create(
            role=users.models.Role.MODERATOR
        )
        self.embroiderer_role = users.models.UserRole.objects.create(
            role=users.models.Role.EMBROIDERER
        )
        self.curier_role = users.models.UserRole.objects.create(
            role=users.models.Role.CURIER
        )

        self.order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.PAID,
            payment_status=catalog.models.PaymentStatus.SUCCEEDED,
            address="Test Address",
            phone="+79991234567",
        )

    def test_list_orders_without_role(self):
        self.client.force_login(self.user)
        response = self.client.get(
            django.urls.reverse("api:staff:orders"),
            {"status": catalog.models.OrderStatus.PAID},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_orders_as_designer(self):
        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse("api:staff:orders"),
            {"status": catalog.models.OrderStatus.PAID},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"]["count"], 1)
        self.assertEqual(
            response.json()["data"]["allowed_statuses"],
            [catalog.models.OrderStatus.PAID],
        )

    def test_list_orders_as_moderator(self):
        self.user.roles.add(self.moderator_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse("api:staff:orders"),
            {"status": catalog.models.OrderStatus.PAID},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.json()["data"]["allowed_statuses"]),
            {
                catalog.models.OrderStatus.PAID,
                catalog.models.OrderStatus.IN_WORK,
                catalog.models.OrderStatus.DRAFT,
            },
        )

    def test_list_orders_without_status(self):
        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.get(django.urls.reverse("api:staff:orders"))

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_orders_with_invalid_status(self):
        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse("api:staff:orders"),
            {"status": "INVALID"},
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class StaffOrderDetailViewTest(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

        self.user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.designer_role = users.models.UserRole.objects.create(
            role=users.models.Role.DESIGNER
        )
        self.embroiderer_role = users.models.UserRole.objects.create(
            role=users.models.Role.EMBROIDERER
        )

        self.order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.PAID,
            payment_status=catalog.models.PaymentStatus.SUCCEEDED,
            address="Test Address",
            phone="+79991234567",
        )

    def test_get_order_detail_without_role(self):
        self.client.force_login(self.user)
        response = self.client.get(
            django.urls.reverse(
                "api:staff:order-detail",
                kwargs={"order_id": self.order.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_order_detail_as_designer(self):
        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse(
                "api:staff:order-detail",
                kwargs={"order_id": self.order.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"]["id"], self.order.id)

    def test_get_nonexistent_order(self):
        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse(
                "api:staff:order-detail",
                kwargs={"order_id": 99999},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_forward_order(self):
        category = catalog.models.Category.objects.create(name="Test Category")
        product = catalog.models.Product.objects.create(name="Test Product")

        from PIL import Image
        import io

        image = Image.new("RGB", (100, 100), color="red")
        image_io = io.BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)

        catalog.models.ProductImage.objects.create(
            product=product,
            image=django.core.files.uploadedfile.SimpleUploadedFile(
                name="test.jpg",
                content=image_io.getvalue(),
                content_type="image/jpeg",
            ),
        )

        catalog.models.ProductEmbroideryFile.objects.create(
            product=product,
            category=category,
            embroidery=django.core.files.uploadedfile.SimpleUploadedFile(
                name="test.jef",
                content=b"test",
            ),
        )

        garment = catalog.models.Garment.objects.create(
            category=category,
            color=catalog.models.Color.objects.create(
                name="Test Color", color="#000000"
            ),
            size=catalog.models.Size.M,
            count=10,
            price=1000,
        )
        order_item = catalog.models.OrderItem.objects.create(
            order=self.order,
            product=product,
            garment=garment,
            quantity=1,
            price=1000,
        )

        self.user.roles.add(self.designer_role)
        self.client.force_login(self.user)

        response = self.client.post(
            django.urls.reverse(
                "api:staff:order-detail",
                kwargs={"order_id": self.order.id},
            ),
            {
                "items": json.dumps(
                    [
                        {
                            "id": order_item.id,
                            "product_id": product.id,
                            "category_id": category.id,
                            "embroidery": None,
                        }
                    ]
                ),
            },
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, catalog.models.OrderStatus.IN_WORK)

    def test_return_order(self):
        self.order.status = catalog.models.OrderStatus.IN_WORK
        self.order.save()

        self.user.roles.add(self.embroiderer_role)
        self.client.force_login(self.user)

        response = self.client.delete(
            django.urls.reverse(
                "api:staff:order-detail",
                kwargs={"order_id": self.order.id},
            ),
            json.dumps({"error_comment": "Test return comment"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, catalog.models.OrderStatus.PAID)


class OrderLogListViewTest(django.test.TestCase):
    def setUp(self):
        self.client = django.test.Client()

        self.user = users.models.User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.moderator_role = users.models.UserRole.objects.create(
            role=users.models.Role.MODERATOR
        )

        self.order = catalog.models.Order.objects.create(
            user=self.user,
            status=catalog.models.OrderStatus.PAID,
            payment_status=catalog.models.PaymentStatus.SUCCEEDED,
            address="Test Address",
            phone="+79991234567",
        )

        self.log = staff.models.OrderLog.objects.create(
            order=self.order,
            user=self.user,
            from_status=catalog.models.OrderStatus.WAITING_PAYMENT,
            to_status=catalog.models.OrderStatus.PAID,
        )

    def test_get_logs_without_role(self):
        self.client.force_login(self.user)
        response = self.client.get(
            django.urls.reverse(
                "api:staff:order-logs",
                kwargs={"order_id": self.order.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_logs_as_moderator(self):
        self.user.roles.add(self.moderator_role)
        self.client.force_login(self.user)

        response = self.client.get(
            django.urls.reverse(
                "api:staff:order-logs",
                kwargs={"order_id": self.order.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["data"]["count"], 1)
        self.assertEqual(
            response.json()["data"]["results"][0]["from_status_display"],
            "Ожидает оплаты",
        )
