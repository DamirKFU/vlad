import django.db
import django.shortcuts
import rest_framework.decorators
import rest_framework.generics
import rest_framework.pagination
import rest_framework.permissions
import rest_framework.response
import rest_framework.status
import rest_framework.views

import catalog.models
import catalog.pagination
import catalog.serializers
import catalog.utils


class GarmentListView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        garments_data = catalog.models.Garment.objects.all_items()
        data = catalog.utils.get_structured_garments(garments_data)
        return rest_framework.response.Response(data)


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
            return rest_framework.response.Response(
                {"id": constructor_product.id},
                status=rest_framework.status.HTTP_201_CREATED,
            )

        return rest_framework.response.Response(
            serializer.errors,
            status=rest_framework.status.HTTP_400_BAD_REQUEST,
        )


class ProductListView(rest_framework.generics.ListAPIView):
    permission_classes = (rest_framework.permissions.AllowAny,)
    serializer_class = catalog.serializers.ProductSerializer
    queryset = catalog.models.Product.objects.all()
    pagination_class = catalog.pagination.ProductPagination


class ProductDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, product_id, *args, **kwargs):
        product = django.shortcuts.get_object_or_404(
            catalog.models.Product.objects, id=product_id
        )

        garments_data = product.garments.items_by_product_detail(product)
        result = {
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "garments": catalog.utils.get_structured_garments(garments_data),
            "images": catalog.utils.get_structured_images(
                product, garments_data, request
            ),
        }
        return rest_framework.response.Response(result)


class AddToCartView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = catalog.serializers.AddToCartSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.validated_data["product"]
            garment = serializer.validated_data["garment"]

            cart, _ = catalog.models.Cart.objects.get_or_create(
                user=request.user
            )
            cart_item, created = catalog.models.CartItem.objects.get_or_create(
                product=product,
                garment=garment,
                cart=cart,
            )

            if not created:
                cart_item.quantity += 1
                cart_item.save()

            return rest_framework.response.Response(
                {
                    "message": "Товар успешно добавлен в корзину",
                    "quantity": cart_item.quantity,
                    "total_price": (product.price + garment.price)
                    * cart_item.quantity,
                },
                status=rest_framework.status.HTTP_201_CREATED,
            )

        return rest_framework.response.Response(
            serializer.errors,
            status=rest_framework.status.HTTP_400_BAD_REQUEST,
        )


class CartView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        cart = django.shortcuts.get_object_or_404(
            catalog.models.Cart.objects.get_cart_with_items(),
            user=request.user,
        )

        cart_items = []
        for item in cart.items.all():
            cart_items.append(
                {
                    "id": item.id,
                    "product_id": item.product.id,
                    "garment_id": item.garment.id,
                    "name": item.product.name,
                    "category": item.garment.category.name,
                    "color": item.garment.color.color,
                    "size": item.garment.size,
                    "quantity": item.quantity,
                    "available_quantity": item.garment.count,
                    "price": item.product.price + item.garment.price,
                    "total_price": item.total_price,
                    "image": (
                        request.build_absolute_uri(
                            item.product.image.image.url
                        )
                        if hasattr(item.product, "image")
                        else None
                    ),
                }
            )

        return rest_framework.response.Response(cart_items)

    @django.db.transaction.atomic
    def delete(self, request, *args, **kwargs):
        item_id = request.data.get("item_id")
        if not item_id:
            return rest_framework.response.Response(
                {"error": "item_id is required"},
                status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        cart = django.shortcuts.get_object_or_404(
            catalog.models.Cart, user=request.user
        )

        try:
            cart_item = cart.items.get(id=item_id)
            cart.items.remove(cart_item)
            cart_item.delete()
            return rest_framework.response.Response(
                {"message": "Товар успешно удален из корзины"}
            )
        except catalog.models.CartItem.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )


class UpdateCartItemView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    def patch(self, request, item_id, *args, **kwargs):
        quantity = request.data.get("quantity")
        if not quantity or int(quantity) < 1:
            return rest_framework.response.Response(
                {"error": "Некорректное количество"},
                status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        try:
            cart_item = catalog.models.CartItem.objects.get(
                cart__user=request.user, id=item_id
            )

            cart_item.quantity = int(quantity)
            cart_item.save()

            return rest_framework.response.Response(
                {
                    "message": "Количество товара успешно обновлено",
                    "quantity": cart_item.quantity,
                    "total_price": cart_item.total_price,
                }
            )

        except catalog.models.CartItem.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, item_id, *args, **kwargs):
        try:
            cart_item = catalog.models.CartItem.objects.get(
                cart__user=request.user, id=item_id
            )
            cart_item.delete()

            return rest_framework.response.Response(
                {"message": "Товар успешно удален из корзины"}
            )
        except catalog.models.CartItem.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )


class CreateOrderView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = catalog.serializers.CreateOrderSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            order = serializer.save()
            return rest_framework.response.Response(
                {
                    "success": True,
                    "data": {"order_id": order.id, "status": order.status},
                    "error": None,
                },
                status=rest_framework.status.HTTP_201_CREATED,
            )

        return rest_framework.response.Response(
            {
                "success": False,
                "data": None,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Ошибка валидации",
                    "fields": serializer.errors,
                },
            },
            status=rest_framework.status.HTTP_400_BAD_REQUEST,
        )


class OrderHistoryView(rest_framework.generics.ListAPIView):
    permission_classes = [rest_framework.permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            catalog.models.Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(
                "items",
                django.db.models.Prefetch(
                    "items__product",
                    queryset=catalog.models.Product.objects.select_related(
                        "image"
                    ),
                ),
                django.db.models.Prefetch(
                    "items__garment",
                    queryset=catalog.models.Garment.objects.select_related(
                        "category", "color"
                    ),
                ),
            )
        )

    def get(self, request, *args, **kwargs):
        orders = self.get_queryset()

        orders_data = []
        for order in orders:
            order_items = []
            for item in order.items.all():
                order_items.append(
                    {
                        "id": item.id,
                        "product_id": item.product.id,
                        "garment_id": item.garment.id,
                        "name": item.product.name,
                        "category": item.garment.category.name,
                        "color": item.garment.color.color,
                        "size": item.garment.size,
                        "quantity": item.quantity,
                        "price": item.product.price + item.garment.price,
                        "total_price": item.total_price,
                        "image": (
                            request.build_absolute_uri(
                                item.product.image.image.url
                            )
                            if hasattr(item.product, "image")
                            else None
                        ),
                    }
                )

            orders_data.append(
                {
                    "id": order.id,
                    "created_at": order.created_at,
                    "status": order.status,
                    "status_display": order.get_status_display(),
                    "address": order.address,
                    "items": order_items,
                }
            )

        return rest_framework.response.Response(orders_data)


class CancelOrderView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.IsAuthenticated,)

    @django.db.transaction.atomic
    def post(self, request, order_id, *args, **kwargs):
        try:
            order = catalog.models.Order.objects.get(
                user=request.user,
                id=order_id,
                status=catalog.models.OrderStatus.WAITING_PAYMENT,
            )
            order.cancel_order()

            return rest_framework.response.Response(
                {"message": "Заказ успешно отменен"},
                status=rest_framework.status.HTTP_200_OK,
            )
        except catalog.models.Order.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Заказ не найден или не может быть отменен"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )
