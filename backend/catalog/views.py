import celery_once
import django.core.exceptions
import django.db
import django.shortcuts
import django_filters.rest_framework
import rest_framework.decorators
import rest_framework.generics
import rest_framework.pagination
import rest_framework.permissions
import rest_framework.response
import rest_framework.status as status
import rest_framework.views
import rest_framework.viewsets

import catalog.filters
import catalog.models
import catalog.pagination
import catalog.serializers
import catalog.tasks
import catalog.utils
import core.utils


class CategoryListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = catalog.serializers.CategorySerializer
    queryset = catalog.models.Category.objects.all()

    def get(self, request, *args, **kwargs):
        return core.utils.success_response(
            data=super().get(request, *args, **kwargs).data,
            message="Категории успешно получены",
        )


class ColorListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = catalog.serializers.ColorSerializer
    queryset = catalog.models.Color.objects.all()

    def get(self, request, *args, **kwargs):
        return core.utils.success_response(
            data=super().get(request, *args, **kwargs).data,
            message="Цвета успешно получены",
        )


class GarmentListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = catalog.serializers.GarmentSerializer
    queryset = catalog.models.Garment.objects.all_items()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = catalog.filters.GarmentFilter

    def get(self, request, *args, **kwargs):
        return core.utils.success_response(
            data=super().get(request, *args, **kwargs).data,
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
    pagination_class = catalog.pagination.ProductPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = catalog.filters.ProductFilter

    def get_queryset(self):
        return catalog.models.Product.objects.get_filter_product_list(
            self.request.query_params
        )

    def get(self, request, *args, **kwargs):
        responce = super().get(request, *args, **kwargs)
        return core.utils.success_response(
            data=responce.data, message="Продукты успешно получены"
        )


class ProductDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, pk, *args, **kwargs):
        product = catalog.models.Product.objects.product_detail(pk)
        if not product:
            return core.utils.error_response(
                message="Продукт не найден",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = catalog.serializers.ProductDetailSerializer(
            product, context={"request": request}
        )
        return core.utils.success_response(
            data=serializer.data, message="Продукт успешно получен"
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
    queryset = catalog.models.Cart.objects.get_cart_with_items()

    def get(self, request, *args, **kwargs):
        cart, _ = self.queryset.filter(user=request.user).get_or_create(
            user=request.user
        )
        item_serializer = catalog.serializers.CartSerializer(
            cart, context={"request": request}
        )

        return core.utils.success_response(
            data=item_serializer.data, message="Корзина успешно получена"
        )


class UpdateCartItemView(rest_framework.generics.GenericAPIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)
    serializer_class = catalog.serializers.UpdateCartItemSerializer

    @django.db.transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        cart_item = request.user.cart.items.get_cart_item_for_update(
            item_id=pk
        )
        if not cart_item:
            return core.utils.error_response(
                message="Товар не найден в корзине",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        serializer = catalog.serializers.UpdateCartItemSerializer(
            data=request.data,
            context={"cart_item": cart_item},
        )
        if not serializer.is_valid():
            return core.utils.error_response(
                serializer_errors=serializer.errors,
                message="Ошибка валидации",
            )

        return core.utils.success_response(
            data=serializer.save(),
            message="Количество товара успешно обновлено",
        )

    @django.db.transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        cart_item = request.user.cart.items.filter(id=pk).first()

        if not cart_item:
            return core.utils.error_response(
                message="Товар не найден в корзине",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        cart_item.delete()

        return core.utils.success_response(
            message="Товар успешно удален из корзины"
        )


class OrderHistoryView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]
    pagination_class = catalog.pagination.OrderPagination
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = catalog.filters.OrderFilter

    def get_queryset(self):
        return catalog.models.Order.objects.get_orders_with_items(
            user=self.request.user
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return catalog.serializers.CreateOrderSerializer

        return catalog.serializers.OrderSerializer

    def get(self, request, *args, **kwargs):
        responce = super().get(request, *args, **kwargs)

        return core.utils.success_response(
            data=responce.data,
            message="Заказы успешно получены",
        )

    def post(self, request, *args, **kwargs):
        try:
            task = catalog.tasks.create_order_task.delay(
                data=request.data, user_id=request.user.id
            )
        except celery_once.AlreadyQueued:
            return core.utils.error_response(
                message="Задача уже запущена",
                http_status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        return core.utils.success_response(
            data={"task_id": task.id},
            message="Задача создания заказа запущена",
            http_status=status.HTTP_201_CREATED,
        )


class OrderDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def get(self, request, pk, *args, **kwargs):
        order = catalog.models.Order.objects.get_orders_for_detail(
            user=request.user,
            pk=pk,
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

    @django.db.transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        order = catalog.models.Order.objects.filter(
            user=request.user,
            id=pk,
        ).first()

        if not order:
            return core.utils.error_response(
                message="Заказ не найден",
                http_status=status.HTTP_404_NOT_FOUND,
            )

        try:
            order.cancel_order()
        except django.core.exceptions.ValidationError as e:
            return core.utils.error_response(
                message=str(e.message),
            )

        return core.utils.success_response(
            message="Заказ успешно отменен",
        )
