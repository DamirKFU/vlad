import django.shortcuts
import rest_framework.serializers

import catalog.models


class ConstructorProductCreateSerializer(
    rest_framework.serializers.Serializer
):
    item_id = rest_framework.serializers.IntegerField()
    image = rest_framework.serializers.ImageField()
    embroidery_image = rest_framework.serializers.ImageField(required=False)

    def create(self, validated_data):
        item_id = validated_data.pop("item_id")
        image = validated_data.pop("image")
        embroidery_image = validated_data.pop("embroidery_image", None)
        user = self.context["request"].user

        item = django.shortcuts.get_object_or_404(
            catalog.models.Item, id=item_id
        )

        constructor_product = catalog.models.ConstructorProduct.objects.create(
            item=item,
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
