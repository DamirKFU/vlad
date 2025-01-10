import rest_framework.serializers

import catalog.models
import staff.models
import staff.utils


class StaffOrderSerializer(rest_framework.serializers.ModelSerializer):
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
        ]


class StaffOrderDetailSerializer(rest_framework.serializers.ModelSerializer):
    next_status = rest_framework.serializers.SerializerMethodField()
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
            "next_status",
        ]

    def get_next_status(self, obj):
        status_flow = {
            catalog.models.OrderStatus.PAID: (
                catalog.models.OrderStatus.IN_WORK
            ),
            catalog.models.OrderStatus.IN_WORK: (
                catalog.models.OrderStatus.DRAFT
            ),
            catalog.models.OrderStatus.DRAFT: (
                catalog.models.OrderStatus.IN_DELIVERY
            ),
        }
        return status_flow.get(obj.status)


class ForwardOrderSerializer(rest_framework.serializers.ModelSerializer):
    class Meta:
        model = catalog.models.Order
        fields = []

    def forward(self, order, user):
        raise NotImplementedError


class DraftForwardSerializer(ForwardOrderSerializer):
    tracking_code = rest_framework.serializers.CharField(required=True)

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.tracking_code.field.name,
        ]

    def validate_tracking_code(self, value):
        if not value.strip():
            raise rest_framework.serializers.ValidationError(
                "Необходимо указать код отслеживания"
            )

        return value

    def forward(self, order, user):
        order.tracking_code = self.validated_data["tracking_code"]
        staff.utils.handle_status_change(
            order=order,
            new_status=catalog.models.OrderStatus.IN_DELIVERY,
            user=user,
        )


class ReturnOrderSerializer(rest_framework.serializers.ModelSerializer):
    error_comment = rest_framework.serializers.CharField(required=True)

    class Meta:
        model = catalog.models.Order
        fields = [
            "error_comment",
        ]

    def validate_error_comment(self, value):
        if not value.strip():
            raise rest_framework.serializers.ValidationError(
                "Необходимо указать причину возврата"
            )

        return value

    def return_to_status(self, order, user, new_status):
        staff.utils.handle_status_change(
            order=order,
            new_status=new_status,
            user=user,
            error_comment=self.validated_data["error_comment"],
        )


class ProductEmbroiderySerializer(rest_framework.serializers.Serializer):
    product_id = rest_framework.serializers.IntegerField()
    category_id = rest_framework.serializers.IntegerField()
    embroidery = rest_framework.serializers.FileField(allow_null=True)


class PaidForwardSerializer(ForwardOrderSerializer):
    items = ProductEmbroiderySerializer(many=True, required=True)

    class Meta:
        model = catalog.models.Order
        fields = ["items"]

    def validate(self, data):
        order = self.context["order"]
        items_dict = {item.product.id: item for item in order.items.all()}
        for item_data in data["items"]:
            product_id = item_data["product_id"]
            if product_id not in items_dict:
                raise rest_framework.serializers.ValidationError(
                    f"Товар {product_id} не найден в заказе"
                )

        combination_without_embroidery = {
            (item.garment.category.id, item.product.id)
            for item in items_dict.values()
            if item.embroidery is None
        }
        combination_with_embroidery = {
            (item["category_id"], item["product_id"])
            for item in data["items"]
            if item["embroidery"] is not None
        }

        if combination_without_embroidery - combination_with_embroidery:
            raise rest_framework.serializers.ValidationError(
                {"form_error": "Для некоторых не хватает вышивки"}
            )

        return data

    def forward(self, order, user):
        data = self.validated_data
        for item in data["items"]:
            embroidery_file, created = (
                catalog.models.ProductEmbroideryFile.objects.get_or_create(
                    product_id=item["product_id"],
                    category_id=item["category_id"],
                )
            )
            if item["embroidery"] is not None:
                embroidery_file.embroidery = item["embroidery"]

            embroidery_file.save()

        staff.utils.handle_status_change(
            order=order,
            new_status=catalog.models.OrderStatus.IN_WORK,
            user=user,
        )


class InWorkForwardSerializer(ForwardOrderSerializer):
    def forward(self, order, user):
        staff.utils.handle_status_change(
            order=order,
            new_status=catalog.models.OrderStatus.DRAFT,
            user=user,
        )


class InDeliveryForwardSerializer(ForwardOrderSerializer):
    def forward(self, order, user):
        staff.utils.handle_status_change(
            order=order,
            new_status=catalog.models.OrderStatus.DELIVERED,
            user=user,
        )


class PaidOrderSerializer(rest_framework.serializers.ModelSerializer):
    items = rest_framework.serializers.SerializerMethodField()
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
            "items",
        ]

    def get_items(self, obj):
        return [
            {
                "id": item.id,
                "image": (
                    self.context["request"].build_absolute_uri(
                        item.product.image.get_image_660x880().url
                    )
                    if item.product.image
                    else None
                ),
                "embroidery": item.embroidery,
                "size": item.garment.size,
                "category": item.garment.category.name,
                "category_id": item.garment.category.id,
                "product_id": item.product.id,
            }
            for item in obj.items.all()
        ]


class InWorkOrderSerializer(rest_framework.serializers.ModelSerializer):
    items = rest_framework.serializers.SerializerMethodField()
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
            "items",
        ]

    def get_items(self, obj):
        return [
            {
                "id": item.id,
                "image": (
                    self.context["request"].build_absolute_uri(
                        item.product.image.get_image_660x880().url
                    )
                    if item.product.image
                    else None
                ),
                "embroidery": item.embroidery,
                "color": item.garment.color.color,
                "size": item.garment.size,
                "quantity": item.quantity,
            }
            for item in obj.items.all()
        ]


class DraftOrderSerializer(rest_framework.serializers.ModelSerializer):
    tracking_code = rest_framework.serializers.CharField()
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
            catalog.models.Order.tracking_code.field.name,
        ]


class InDeliveryOrderSerializer(rest_framework.serializers.ModelSerializer):
    tracking_code = rest_framework.serializers.CharField()
    status_display = rest_framework.serializers.CharField(
        source=f"get_{catalog.models.Order.status.field.name}_display"
    )

    class Meta:
        model = catalog.models.Order
        fields = [
            catalog.models.Order.id.field.name,
            catalog.models.Order.status.field.name,
            "status_display",
            catalog.models.Order.tracking_code.field.name,
        ]
