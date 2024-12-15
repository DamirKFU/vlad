import django.shortcuts
import rest_framework.serializers

import catalog.models


class ConstructorProductCreateSerializer(
    rest_framework.serializers.Serializer
):
    item_id = rest_framework.serializers.IntegerField()
    image = rest_framework.serializers.ImageField()
    embroidery_image = rest_framework.serializers.ImageField()

    def validate_item_id(self, value):
        item = django.shortcuts.get_object_or_404(
            catalog.models.Item, id=value
        )
        if item.count <= 0:
            raise rest_framework.serializers.ValidationError(
                "Item count is zero or less."
            )

        return value

    def create(self, validated_data):
        item_id = validated_data.pop("item_id")
        image = validated_data.pop("image")
        embroidery_image = validated_data.pop("embroidery_image")
        user = self.context["request"].user

        item = catalog.models.Item.objects.get(id=item_id)
        item.count -= 1
        item.save()

        constructor_product = catalog.models.ConstructorProduct.objects.create(
            item=item,
            user=user,
        )

        catalog.models.ConstructorProductImage.objects.create(
            product=constructor_product, image=image
        )
        catalog.models.ConstructorEmbroideryImage.objects.create(
            product=constructor_product, image=embroidery_image
        )

        return constructor_product
