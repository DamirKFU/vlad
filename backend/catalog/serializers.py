import django.shortcuts
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

        garment = django.shortcuts.get_object_or_404(
            catalog.models.Garment, id=garment_id
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


class AddToCartSerializer(rest_framework.serializers.Serializer):
    id_product = rest_framework.serializers.IntegerField()
    id_garment = rest_framework.serializers.IntegerField()

    def validate(self, data):
        product = django.shortcuts.get_object_or_404(
            catalog.models.Product.objects.only("id"),
            id=data["id_product"],
        )
        garment = django.shortcuts.get_object_or_404(
            catalog.models.Garment.objects.only("id"),
            id=data["id_garment"],
        )

        if (
            not product.garments.values_list("id", flat=True)
            .filter(id=garment.id)
            .exists()
        ):
            raise rest_framework.serializers.ValidationError(
                "Данная одежда не принадлежит этому товару"
            )

        data["product"] = product
        data["garment"] = garment
        return data
