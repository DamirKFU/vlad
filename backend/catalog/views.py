import django.db
import django.shortcuts
import rest_framework.generics
import rest_framework.permissions
import rest_framework.response
import rest_framework.views

import catalog.models
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
    queryset = catalog.models.Product.objects


class ProductDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, product_id, *args, **kwargs):
        product = django.shortcuts.get_object_or_404(
            catalog.models.Product, id=product_id
        )
        garments_data = product.garments.items_by_product(product)
        result = {
            "id": product.id,
            "name": product.name,
            "image": request.build_absolute_uri(product.image.image.url),
            "price": product.price,
            "garments": catalog.utils.get_structured_garments(garments_data),
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
            cart_item, _ = catalog.models.CartItem.objects.get_or_create(
                product=product,
                garment=garment,
            )

            cart_item_quantity, created = (
                catalog.models.CartItemQuantity.objects.get_or_create(
                    cart=cart, item=cart_item, defaults={"quantity": 1}
                )
            )

            if not created:
                cart_item_quantity.quantity += 1
                cart_item_quantity.save()

            return rest_framework.response.Response(
                {
                    "message": "Товар успешно добавлен в корзину",
                    "quantity": cart_item_quantity.quantity,
                    "total_price": (product.price + garment.price)
                    * cart_item_quantity.quantity,
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
        for cart_item_quantity in cart.cartitemquantity_set.all():
            item = cart_item_quantity.item
            total_price = (
                item.product.price + item.garment.price
            ) * cart_item_quantity.quantity

            cart_items.append(
                {
                    "id": item.id,
                    "product_id": item.product.id,
                    "garment_id": item.garment.id,
                    "name": item.product.name,
                    "size": item.garment.size,
                    "category": item.garment.category.name,
                    "color_hex": item.garment.color.color,
                    "product_price": item.product.price,
                    "garment_price": item.garment.price,
                    "quantity": cart_item_quantity.quantity,
                    "total_price": total_price,
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
            cart_item_quantity = (
                catalog.models.CartItemQuantity.objects.select_related(
                    "item__product", "item__garment"
                ).get(cart__user=request.user, item__id=item_id)
            )

            cart_item_quantity.quantity = int(quantity)
            cart_item_quantity.save()

            total_price = (
                cart_item_quantity.item.product.price
                + cart_item_quantity.item.garment.price
            ) * cart_item_quantity.quantity

            return rest_framework.response.Response(
                {
                    "message": "Количество товара успешно обновлено",
                    "quantity": cart_item_quantity.quantity,
                    "total_price": total_price,
                }
            )

        except catalog.models.CartItemQuantity.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )

    def delete(self, request, item_id, *args, **kwargs):
        try:
            cart_item_quantity = catalog.models.CartItemQuantity.objects.get(
                cart__user=request.user, item__id=item_id
            )
            cart_item = cart_item_quantity.item
            cart_item_quantity.delete()
            cart_item.delete()

            return rest_framework.response.Response(
                {"message": "Товар успешно удален из корзины"}
            )
        except catalog.models.CartItemQuantity.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )
