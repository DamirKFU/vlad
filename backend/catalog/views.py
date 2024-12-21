import collections

import django.db
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
