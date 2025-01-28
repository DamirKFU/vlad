import django.db.models
import rest_framework.serializers

import catalog.models
import catalog.tasks
import catalog.utils
import catalog.validators
import payments.services
import staff.logs


ADDITIONAL_IMAGES_RELATED_QUERY_NAME = (
    catalog.models.Product.additional_images.field.related_query_name()
)


class CategorySerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = catalog.models.Category
        fields = [
            catalog.models.Category.id.field.name,
            catalog.models.Category.name.field.name,
        ]


class ColorSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = catalog.models.Color
        fields = [
            catalog.models.Color.id.field.name,
            catalog.models.Color.name.field.name,
            catalog.models.Color.color.field.name,
        ]


class GarmentSerializer(rest_framework.serializers.ModelSerializer):
    category = CategorySerializer()
    color = ColorSerializer()

    class Meta:
        model = catalog.models.Garment
        fields = [
            catalog.models.Garment.id.field.name,
            catalog.models.Garment.category.field.name,
            catalog.models.Garment.color.field.name,
            catalog.models.Garment.size.field.name,
            catalog.models.Garment.count.field.name,
            catalog.models.Garment.price.field.name,
        ]


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


class ProductSerializer(rest_framework.serializers.ModelSerializer):
    main_image = rest_framework.serializers.SerializerMethodField()
    secondary_image = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.Product
        fields = [
            catalog.models.Product.id.field.name,
            catalog.models.Product.name.field.name,
            catalog.models.Product.main_image.related.name,
            catalog.models.Product.secondary_image.related.name,
            catalog.models.Product.price.field.name,
        ]

    def get_main_image(self, obj):
        if hasattr(obj, "main_image") and obj.main_image:
            return obj.main_image.get_image_660x880().url

        return None

    def get_secondary_image(self, obj):
        if hasattr(obj, "secondary_image") and obj.secondary_image:
            return obj.secondary_image.get_image_660x880().url

        return None


class ProductAdditionalImageSerializer(
    rest_framework.serializers.ModelSerializer
):
    image = rest_framework.serializers.SerializerMethodField()
    category = rest_framework.serializers.SerializerMethodField()
    color = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.ProductAdditionalImage
        fields = [
            catalog.models.ProductAdditionalImage.image.field.name,
            catalog.models.ProductAdditionalImage.category.field.name,
            catalog.models.ProductAdditionalImage.color.field.name,
        ]

    def get_image(self, obj):
        if hasattr(obj, "image"):
            return obj.image.url

        return None

    def get_category(self, obj):
        return {
            catalog.models.Category.id.field.name: obj.category.id,
            catalog.models.Category.name.field.name: obj.category.name,
        }

    def get_color(self, obj):
        return {
            catalog.models.Color.id.field.name: obj.color.id,
            catalog.models.Color.name.field.name: obj.color.name,
        }


class ProductDetailSerializer(rest_framework.serializers.ModelSerializer):
    main_image = rest_framework.serializers.SerializerMethodField()
    additional_images = ProductAdditionalImageSerializer(
        many=True, read_only=True
    )
    garments = GarmentSerializer(many=True, read_only=True)

    class Meta:
        model = catalog.models.Product
        fields = [
            catalog.models.Product.id.field.name,
            catalog.models.Product.name.field.name,
            catalog.models.Product.price.field.name,
            catalog.models.Product.main_image.related.name,
            ADDITIONAL_IMAGES_RELATED_QUERY_NAME,
            catalog.models.Product.garments.field.name,
        ]

    def get_main_image(self, obj):
        if hasattr(obj, "main_image"):
            return obj.main_image.image.url

        return None


class CartItemSerializer(rest_framework.serializers.ModelSerializer):
    product = ProductSerializer()
    garment = GarmentSerializer()

    class Meta:
        model = catalog.models.CartItem
        fields = [
            catalog.models.CartItem.id.field.name,
            catalog.models.CartItem.quantity.field.name,
            catalog.models.CartItem.product.field.name,
            catalog.models.CartItem.garment.field.name,
            "total_price",
        ]


class CartSerializer(rest_framework.serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = catalog.models.Cart
        fields = [
            catalog.models.Cart.id.field.name,
            catalog.models.Cart.items.field.related_query_name(),
        ]


class AddToCartSerializer(rest_framework.serializers.Serializer):
    id_product = rest_framework.serializers.IntegerField()
    id_garment = rest_framework.serializers.IntegerField()

    def validate(self, data):
        errors = {}
        product = catalog.models.Product.objects.get_product_for_cart(
            data["id_product"]
        )
        if not product:
            errors["id_product"] = "Продукт не найден"

        garment = catalog.models.Garment.objects.get_garment_for_cart(
            data["id_garment"]
        )
        if not garment:
            errors["id_garment"] = "Одежда не найдена"

        if errors:
            raise rest_framework.serializers.ValidationError(errors)

        if not catalog.models.Product.objects.check_garment_belongs_to_product(
            data["id_product"], data["id_garment"]
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
            defaults={catalog.models.CartItem.quantity.field.name: 1},
        )

        if not created:
            cart_item.quantity = (
                django.db.models.F(catalog.models.CartItem.quantity.field.name)
                + 1
            )
            cart_item.save()
            cart_item.refresh_from_db()

        return {
            "quantity": cart_item.quantity,
            "total_price": (product.price + garment.price)
            * cart_item.quantity,
        }


class CreateOrderSerializer(rest_framework.serializers.Serializer):
    address = rest_framework.serializers.CharField(required=True)
    phone = rest_framework.serializers.CharField(
        required=True, validators=[catalog.validators.validate_russian_phone]
    )

    def validate(self, data):
        user_id = self.context["user_id"]
        cart = catalog.models.Cart.objects.get_cart_for_order(user_id=user_id)

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

        cart_items = list(cart.items.all())
        if not cart_items:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Корзина пуста"}
            )

        garments_ids = [cart_item.garment_id for cart_item in cart_items]
        garments = list(
            catalog.models.Garment.objects.filter(id__in=garments_ids)
            .select_for_update()
            .all()
        )
        garments_dict = {garment.id: garment for garment in garments}

        for cart_item in cart_items:
            garment = garments_dict[cart_item.garment_id]
            if garment.count < cart_item.quantity:
                raise rest_framework.serializers.ValidationError(
                    {"count": "Недостаточно товара"}
                )

        data["items"] = cart_items
        data["garments"] = garments_dict
        return data

    def create(self, validated_data):
        order = catalog.models.Order.objects.create(
            user_id=self.context["user_id"],
            address=validated_data["address"],
            phone=validated_data["phone"],
        )

        def create_order_item_and_update_garment(item, order):
            garment = validated_data["garments"][item.garment_id]
            order_item = catalog.models.OrderItem(
                order=order,
                product=item.product,
                garment=garment,
                quantity=item.quantity,
                price=item.product.price + garment.price,
            )
            garment.count = (
                django.db.models.F(catalog.models.Garment.count.field.name)
                - item.quantity
            )
            return order_item, garment

        order_items, garments = zip(
            *[
                create_order_item_and_update_garment(item, order)
                for item in validated_data["items"]
            ]
        )

        catalog.models.OrderItem.objects.bulk_create(order_items)
        catalog.models.Garment.objects.bulk_update(
            garments,
            [catalog.models.Garment.count.field.name],
        )
        order.total_sum = sum(item.total_price for item in order_items)
        yookassa_service = payments.services.YooKassaService()
        payment_data = yookassa_service.create_payment(
            order=order,
            return_url=f"http://localhost:3000/orders/{order.id}",
        )

        order.payment_id = payment_data["id"]
        order.confirmation_url = payment_data["confirmation_url"]
        order.payment_status = payment_data["status"]
        order.save()

        return order


class OrderItemSerializer(rest_framework.serializers.ModelSerializer):
    product = ProductSerializer()
    garment = GarmentSerializer()

    class Meta:
        model = catalog.models.OrderItem
        fields = [
            catalog.models.OrderItem.id.field.name,
            catalog.models.OrderItem.product.field.name,
            catalog.models.OrderItem.garment.field.name,
            catalog.models.OrderItem.quantity.field.name,
            catalog.models.OrderItem.price.field.name,
            "total_price",
        ]


class OrderSerializer(rest_framework.serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            catalog.models.Order.address.field.name,
            catalog.models.Order.total_sum.field.name,
            catalog.models.Order.items.field.related_query_name(),
        ]

    def get_status(self, obj):
        return {
            "status": obj.status,
            "status_display": obj.get_status_display(),
        }


class UpdateCartItemSerializer(rest_framework.serializers.Serializer):
    quantity = rest_framework.serializers.IntegerField(
        min_value=1,
        error_messages={
            "min_value": "Некорректное количество",
            "invalid": "Некорректное количество",
        },
    )

    def validate(self, data):
        cart_item = self.context["cart_item"]

        if cart_item.garment.count < data["quantity"]:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Недостаточно товара на складе"}
            )

        data["cart_item"] = cart_item
        return data

    def save(self):
        quantity = self.validated_data["quantity"]
        cart_item = self.validated_data["cart_item"]
        cart_item.quantity = quantity
        cart_item.save(
            update_fields=[catalog.models.CartItem.quantity.field.name]
        )

        return {
            "quantity": quantity,
            "total_price": cart_item.total_price,
        }


class OrderDetailSerializer(rest_framework.serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    confirmation_url = rest_framework.serializers.SerializerMethodField()
    status = rest_framework.serializers.SerializerMethodField()

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            catalog.models.Order.address.field.name,
            catalog.models.Order.phone.field.name,
            catalog.models.Order.total_sum.field.name,
            catalog.models.Order.items.field.related_query_name(),
            catalog.models.Order.confirmation_url.field.name,
        ]

    def get_status(self, obj):
        return {
            "status": obj.status,
            "status_display": obj.get_status_display(),
        }

    def to_representation(self, instance):
        status = instance.status
        if status != catalog.models.OrderStatus.WAITING_PAYMENT:
            return super().to_representation(instance)

        status_payment = (
            payments.services.YooKassaService().get_status_payment(
                instance.payment_id
            )
        )
        instance.payment_status = status_payment
        if status_payment == catalog.models.PaymentStatus.SUCCEEDED:
            staff.logs.log_order_status_change(
                instance,
                None,
                instance.status,
                catalog.models.OrderStatus.PAID,
            )

            staff.logs.log_order_status_change(
                instance,
                None,
                catalog.models.OrderStatus.PAID,
                catalog.models.OrderStatus.IN_WORK,
            )
            instance.status = catalog.models.OrderStatus.IN_WORK

        if status_payment == catalog.models.PaymentStatus.CANCELED:
            staff.logs.log_order_status_change(
                instance,
                None,
                instance.status,
                catalog.models.OrderStatus.CANCELED,
            )
            instance.status = catalog.models.OrderStatus.CANCELED

        instance.save(
            update_fields=[
                catalog.models.Order.status.field.name,
                catalog.models.Order.payment_status.field.name,
            ]
        )

        return super().to_representation(instance)

    def get_confirmation_url(self, obj):
        if obj.status == catalog.models.OrderStatus.WAITING_PAYMENT:
            return obj.confirmation_url

        return None
