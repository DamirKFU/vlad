import rest_framework.serializers

import catalog.models
import catalog.utils
import catalog.validators


class ConstructorProductCreateSerializer(
    rest_framework.serializers.Serializer
):
    garment_id = rest_framework.serializers.IntegerField()
    image = rest_framework.serializers.ImageField(
        validators=[catalog.validators.validate_file_size]
    )
    embroidery_image = rest_framework.serializers.ImageField(
        required=False,
        validators=[catalog.validators.validate_file_size],
    )

    def create(self, validated_data):
        garment_id = validated_data.pop("garment_id")
        image = validated_data.pop("image")
        embroidery_image = validated_data.pop("embroidery_image", None)
        user = self.context["request"].user

        garment = catalog.models.Garment.objects.filter(id=garment_id).first()

        if not garment:
            raise rest_framework.serializers.ValidationError(
                {"garment_id": "Одежда не найдена"}
            )

        constructor_product = catalog.models.ConstructorProduct.objects.create(
            garment=garment,
            user=user,
        )

        catalog.models.ConstructorProductImage.objects.create(
            product=constructor_product, image=image
        )
        if embroidery_image:
            catalog.models.ConstructorEmbroideryImage.objects.create(
                product=constructor_product,
                image=embroidery_image,
            )

        return constructor_product


class CategorySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = catalog.models.Category
        fields = ["name"]


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    image = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.Product
        fields = [
            "id",
            "name",
            "image",
            "price",
        ]

    def get_image(self, obj):
        if hasattr(obj, "image") and obj.image:
            request = self.context.get("request")
            return request.build_absolute_uri(
                obj.image.get_image_660x880().url
            )

        return None


class CartSerializer(rest_framework.serializers.Serializer):
    def validate(self, data):
        cart = (
            catalog.models.Cart.objects.get_cart_with_items()
            .filter(user=self.context["request"].user)
            .first()
        )

        if not cart:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Корзина не найдена"}
            )

        data["cart"] = cart
        return data


class AddToCartSerializer(rest_framework.serializers.Serializer):
    id_product = rest_framework.serializers.IntegerField()
    id_garment = rest_framework.serializers.IntegerField()

    def validate(self, data):
        errors = {}
        product = (
            catalog.models.Product.objects.filter(id=data["id_product"])
            .only(
                "name",
                "price",
            )
            .first()
        )
        if not product:
            errors["id_product"] = "Продукт не найден"

        garment = (
            catalog.models.Garment.objects.filter(id=data["id_garment"])
            .only(
                "price",
            )
            .first()
        )
        if not garment:
            errors["id_garment"] = "Одежда не найдена"

        if errors:
            raise rest_framework.serializers.ValidationError(errors)

        if (
            not product.garments.values_list("id", flat=True)
            .filter(id=garment.id)
            .exists()
        ):
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Данная одежда не принадлежит этому товару"}
            )

        data["product"] = product
        data["garment"] = garment
        return data

    def create(self, validated_data):
        product = validated_data["product"]
        garment = validated_data["garment"]
        user = self.context["request"].user

        cart, _ = catalog.models.Cart.objects.get_or_create(user=user)
        cart_item, created = catalog.models.CartItem.objects.get_or_create(
            product=product,
            garment=garment,
            cart=cart,
            defaults={"quantity": 1},
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return {
            "quantity": cart_item.quantity,
            "total_price": (product.price + garment.price)
            * cart_item.quantity,
        }


class DeleteCartItemSerializer(rest_framework.serializers.Serializer):
    item_id = rest_framework.serializers.IntegerField()

    def validate(self, data):
        cart = self.context["request"].user.cart
        cart_item = cart.items.filter(id=data["item_id"]).first()
        if not cart_item:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Товар не найден в корзине"}
            )

        data["cart_item"] = cart_item
        return data

    def create(self, validated_data):
        cart_item = validated_data["cart_item"]
        cart_item.delete()
        return cart_item


class CartItemSerializer(rest_framework.serializers.ModelSerializer):
    name = rest_framework.serializers.CharField(source="product.name")
    category = rest_framework.serializers.CharField(
        source="garment.category.name"
    )
    color = rest_framework.serializers.CharField(source="garment.color.color")
    size = rest_framework.serializers.CharField(source="garment.size")
    available_quantity = rest_framework.serializers.IntegerField(
        source="garment.count"
    )
    price = rest_framework.serializers.SerializerMethodField()
    image = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.CartItem
        fields = [
            "id",
            "name",
            "category",
            "color",
            "size",
            "quantity",
            "available_quantity",
            "price",
            "total_price",
            "image",
        ]

    def get_price(self, obj):
        return obj.product.price + obj.garment.price

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.matching_image:
            image = catalog.models.ProductAdditionalImage(
                image=obj.matching_image
            )
            return request.build_absolute_uri(image.get_image_330x440().url)

        return None


class CreateOrderSerializer(rest_framework.serializers.Serializer):
    address = rest_framework.serializers.CharField(required=True)
    phone = rest_framework.serializers.CharField(
        required=True, validators=[catalog.validators.validate_russian_phone]
    )

    def validate(self, data):
        user = self.context["request"].user
        cart = catalog.models.Cart.objects.get_cart_for_order(user=user)

        if cart is None:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Корзина не найдена"}
            )

        if cart.user.orders.filter(
            status=catalog.models.OrderStatus.WAITING_PAYMENT
        ).exists():
            raise rest_framework.serializers.ValidationError(
                {"form_error": "У вас уже есть заказ в ожидании оплаты."}
            )

        cart_items = cart.items.all()
        if not cart_items:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Корзина пуста"}
            )

        for cart_item in cart_items:
            garment = cart_item.garment
            if garment.count < cart_item.quantity:
                raise rest_framework.serializers.ValidationError(
                    {"form_error": f"Недостаточно товара для {cart_item.id}"}
                )

        data["cart"] = cart
        return data

    def create(self, validated_data):
        order = catalog.models.Order.objects.create(
            user=validated_data["cart"].user,
            address=validated_data["address"],
            phone=validated_data["phone"],
        )

        def create_order_item_and_update_garment(item, order):
            garment = item.garment
            return (
                catalog.models.OrderItem(
                    order=order,
                    product=item.product,
                    garment=garment,
                    quantity=item.quantity,
                    price=item.product.price + garment.price,
                ),
                setattr(
                    garment,
                    catalog.models.Garment.count.field.name,
                    garment.count - item.quantity,
                )
                or garment,
            )

        order_items, garments = zip(
            *[
                create_order_item_and_update_garment(item, order)
                for item in validated_data["cart"].items.all()
            ]
        )

        catalog.models.OrderItem.objects.bulk_create(order_items)
        catalog.models.Garment.objects.bulk_update(
            garments,
            [catalog.models.Garment.count.field.name],
        )

        return order


class OrderItemSerializer(rest_framework.serializers.ModelSerializer):
    name = rest_framework.serializers.CharField(source="product.name")
    category = rest_framework.serializers.CharField(
        source="garment.category.name"
    )
    color = rest_framework.serializers.CharField(source="garment.color.color")
    size = rest_framework.serializers.CharField(source="garment.size")
    image = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.OrderItem
        fields = [
            "name",
            "category",
            "color",
            "size",
            "quantity",
            "price",
            "total_price",
            "image",
        ]

    def get_image(self, obj):
        request = self.context.get("request")
        if obj.matching_image:
            image = catalog.models.ProductAdditionalImage(
                image=obj.matching_image
            )
            return request.build_absolute_uri(image.get_image_330x440().url)

        return None


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = rest_framework.serializers.CharField(
        source="get_status_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            "id",
            "status",
            "status_display",
            "address",
            "items",
        ]


class UpdateCartItemSerializer(rest_framework.serializers.Serializer):
    item_id = rest_framework.serializers.IntegerField()
    quantity = rest_framework.serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Некорректное количество",
            "invalid": "Некорректное количество",
        },
    )

    def validate(self, data):
        cart_item = (
            catalog.models.CartItem.objects.select_related(
                "garment",
                "product",
            )
            .filter(
                cart__user=self.context["request"].user,
                id=data["item_id"],
            )
            .only(
                "quantity",
                "garment__count",
                "garment__price",
                "product__price",
            )
            .first()
        )

        if not cart_item:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Товар не найден в корзине"}
            )

        if cart_item.garment.count < data["quantity"]:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Недостаточно товара на складе"}
            )

        data["cart_item"] = cart_item
        return data

    def update(self, instance, validated_data):
        quantity = validated_data["quantity"]
        catalog.models.CartItem.objects.filter(id=instance.id).update(
            quantity=quantity
        )

        instance.quantity = quantity

        return {
            "quantity": quantity,
            "total_price": instance.total_price,
        }


class CancelOrderSerializer(rest_framework.serializers.Serializer):
    order_id = rest_framework.serializers.IntegerField()

    def validate(self, data):
        order = catalog.models.Order.objects.filter(
            user=self.context["request"].user,
            id=data["order_id"],
            status=catalog.models.OrderStatus.WAITING_PAYMENT,
        ).first()

        if not order:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Заказ не найден или не может быть отменен"}
            )

        data["order"] = order
        return data

    def create(self, validated_data):
        order = validated_data["order"]
        order.cancel_order()
        return order
