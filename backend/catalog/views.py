import collections

import django.db
import django.shortcuts
import rest_framework.generics
import rest_framework.permissions
import rest_framework.response
import rest_framework.views

import catalog.models
import catalog.serializers


class GarmentListView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        garments = catalog.models.Garment.objects.all_items()
        result = collections.defaultdict(lambda: collections.defaultdict(dict))
        category_name_key = (
            f"{catalog.models.Garment.category.field.name}"
            f"__{catalog.models.Category.name.field.name}"
        )
        size_key = catalog.models.Garment.size.field.name
        count_key = catalog.models.Garment.count.field.name
        garment_id_key = catalog.models.Garment.id.field.name
        color_name_key = (
            f"{catalog.models.Garment.color.field.name}"
            f"__{catalog.models.Color.name.field.name}"
        )
        color_color_key = (
            f"{catalog.models.Garment.color.field.name}"
            f"__{catalog.models.Color.color.field.name}"
        )
        for garment in garments:
            category_name = garment[category_name_key]
            size = garment[size_key]
            color_name = garment[color_name_key]
            count = garment[count_key]
            hex_color = garment[color_color_key]
            garment_id = garment[garment_id_key]

            result[category_name][size][color_name] = {
                "count": count,
                "hex": hex_color,
                "id": garment_id,
            }

        return rest_framework.response.Response(result)


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
    queryset = catalog.models.Product.objects.all_items()


class ProductDetailView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, product_id, *args, **kwargs):
        product = django.shortcuts.get_object_or_404(
            catalog.models.Product.objects.detail_view(), id=product_id
        )
        related_garments = catalog.models.Garment.objects.items_by_category(
            product.category
        )

        result = {
            "id": product.id,
            "name": product.name,
            "image": request.build_absolute_uri(product.image.image.url),
            "price": product.price,
            "garments": collections.defaultdict(
                lambda: collections.defaultdict(dict)
            ),
        }

        size_key = catalog.models.Garment.size.field.name
        count_key = catalog.models.Garment.count.field.name
        garment_id_key = catalog.models.Garment.id.field.name
        color_name_key = (
            f"{catalog.models.Garment.color.field.name}"
            f"__{catalog.models.Color.name.field.name}"
        )
        color_color_key = (
            f"{catalog.models.Garment.color.field.name}"
            f"__{catalog.models.Color.color.field.name}"
        )

        for garment in related_garments:
            size = garment[size_key]
            color_name = garment[color_name_key]
            count = garment[count_key]
            hex_color = garment[color_color_key]
            garment_id = garment[garment_id_key]

            result["garments"][size][color_name] = {
                "count": count,
                "hex": hex_color,
                "id": garment_id,
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

            cart_item = catalog.models.CartItem.objects.create(
                product=product,
                garment=garment,
                quantity=1,
            )

            cart.items.add(cart_item)

            return rest_framework.response.Response(
                {"message": "Товар успешно добавлен в корзину"},
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
            catalog.models.Cart, user=request.user
        )

        cart_items = []
        for item in cart.items.all():
            cart_items.append(
                {
                    "id": item.id,
                    "product_id": item.product.id,
                    "garment_id": item.garment.id,
                    "name": item.product.name,
                    "size": item.garment.size,
                    "color": item.garment.color.name,
                    "color_hex": item.garment.color.color,
                    "price": item.product.price,
                    "quantity": item.quantity,
                    "total_price": item.product.price * item.quantity,
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
        if not quantity:
            return rest_framework.response.Response(
                {"error": "quantity is required"},
                status=rest_framework.status.HTTP_400_BAD_REQUEST,
            )

        cart = django.shortcuts.get_object_or_404(
            catalog.models.Cart, user=request.user
        )

        try:
            cart_item = cart.items.get(id=item_id)
            cart_item.quantity = quantity
            cart_item.save()

            return rest_framework.response.Response(
                {
                    "message": "Количество товара успешно обновлено",
                    "quantity": cart_item.quantity,
                    "total_price": cart_item.product.price
                    * cart_item.quantity,
                }
            )
        except catalog.models.CartItem.DoesNotExist:
            return rest_framework.response.Response(
                {"error": "Товар не найден в корзине"},
                status=rest_framework.status.HTTP_404_NOT_FOUND,
            )
