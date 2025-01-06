import django.db
import django.shortcuts
import rest_framework.decorators
import rest_framework.generics
import rest_framework.pagination
import rest_framework.permissions
import rest_framework.response
import rest_framework.status as status
import rest_framework.views

import catalog.models
import catalog.pagination
import catalog.serializers
import catalog.tasks
import catalog.utils
import core.utils


class GarmentListView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        garments_data = catalog.models.Garment.objects.all_items()
        data = catalog.utils.get_structured_garments(garments_data)
        return core.utils.success_response(
            data=data,
            message="Одежда успешно получена",
        )


class ConstructorProductCreateView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = catalog.serializers.ConstructorProductCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid():
            constructor_product = serializer.save()
            return core.utils.success_response(
                data={"id": constructor_product.id},
                message="Конструктор успешно создан",
                http_status=status.HTTP_201_CREATED,
            )

        return core.utils.error_response(
            serializer_errors=serializer.errors,
            message="Ошибка валидации",
        )


class ProductListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = catalog.serializers.ProductSerializer
    queryset = catalog.models.Product.objects.all()
    pagination_class = catalog.pagination.ProductPagination

    def get(self, request, *args, **kwargs):
        responce = super().get(request, *args, **kwargs)
        return core.utils.success_response(
            data=responce.data, message="Продукты успешно получены"
        )


class ProductDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, product_id, *args, **kwargs):
        product = (
            catalog.models.Product.objects.select_related(
                catalog.models.Product.image.related.name
            )
            .filter(id=product_id)
            .first()
        )
        if not product:
            return core.utils.error_response(
                message="Продукт не найден",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        garments_data = product.garments.items_by_product_detail(product)
        result = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "image": self.request.build_absolute_uri(product.image.image.url),
            "garments": catalog.utils.get_structured_garments(garments_data),
            "images": catalog.utils.get_structured_images(
                product, garments_data, request
            ),
        }
        return core.utils.success_response(
            data=result, message="Продукт успешно получен"
        )


class AddToCartView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = catalog.serializers.AddToCartSerializer

    @django.db.transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = catalog.serializers.AddToCartSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
            )

        return core.utils.success_response(
            data=serializer.save(),
            message="Товар успешно добавлен в корзину",
            http_status=status.HTTP_201_CREATED,
        )


class CartView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cart_serializer = catalog.serializers.CartSerializer(
            data={}, context={"request": request}
        )
        if not cart_serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=cart_serializer.errors,
                message="Ошибка валидации",
            )

        cart = cart_serializer.validated_data["cart"]

        item_serializer = catalog.serializers.CartItemSerializer(
            cart.items.all(), many=True, context={"request": request}
        )

        return core.utils.success_response(
            data=item_serializer.data, message="Корзина успешно получена"
        )


class UpdateCartItemView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def patch(self, request, *args, **kwargs):
        serializer = catalog.serializers.UpdateCartItemSerializer(
            data=request.data,
            context={"request": request},
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
            )

        return core.utils.success_response(
            data=serializer.update(
                serializer.validated_data["cart_item"],
                serializer.validated_data,
            ),
            message="Количество товара успешно обновлено",
        )

    @django.db.transaction.atomic
    def delete(self, request, *args, **kwargs):
        serializer = catalog.serializers.DeleteCartItemSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors, message="Ошибка валидации"
            )

        serializer.save()

        return core.utils.success_response(
            message="Товар успешно удален из корзины"
        )


class CreateOrderView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = catalog.serializers.CreateOrderSerializer

    def post(self, request, *args, **kwargs):
        task = catalog.tasks.create_order_task.delay(
            data=request.data, user_id=request.user.id
        )

        return core.utils.success_response(
            data={"task_id": task.id},
            message="Задача создания заказа запущена",
            http_status=status.HTTP_201_CREATED,
        )


class OrderHistoryView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    pagination_class = catalog.pagination.OrderPagination
    serializer_class = catalog.serializers.OrderSerializer

    def get_queryset(self):
        return catalog.models.Order.objects.get_orders_with_items(
            user=self.request.user
        )

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            page, many=True, context={"request": request}
        )

        return core.utils.success_response(
            data=self.get_paginated_response(serializer.data).data,
            message="Заказы успешно получены",
        )

    @django.db.transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = catalog.serializers.CancelOrderSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
            )

        serializer.save()
        return core.utils.success_response(
            message="Заказ успешно отменен",
        )


class OrderDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def get(self, request, order_id, *args, **kwargs):
        order = (
            catalog.models.Order.objects.get_orders_for_detail(
                user=request.user,
            )
            .filter(
                id=order_id,
            )
            .first()
        )

        if not order:
            return core.utils.error_response(
                message="Заказ не найден",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = catalog.serializers.OrderDetailSerializer(
            order,
            context={"request": request},
        )

        return core.utils.success_response(
            data=serializer.data,
            message="Заказ успешно получен",
        )
