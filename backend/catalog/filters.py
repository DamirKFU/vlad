import django_filters
import django_filters.rest_framework

import catalog.models


class ProductFilter(django_filters.rest_framework.FilterSet):
    category = django_filters.CharFilter(
        field_name=(
            f"{catalog.models.Product.garments.field.name}__"
            f"{catalog.models.Garment.category.field.name}__"
            f"{catalog.models.Category.name.field.name}"
        ),
        max_length=255,
        lookup_expr="exact",
    )
    color = django_filters.CharFilter(
        field_name=(
            f"{catalog.models.Product.garments.field.name}__"
            f"{catalog.models.Garment.color.field.name}__"
            f"{catalog.models.Color.name.field.name}"
        ),
        lookup_expr="exact",
    )
    size = django_filters.CharFilter(
        field_name=(
            f"{catalog.models.Product.garments.field.name}__"
            f"{catalog.models.Garment.size.field.name}"
        ),
        lookup_expr="exact",
    )
    count = django_filters.NumberFilter(
        field_name=(
            f"{catalog.models.Product.garments.field.name}__"
            f"{catalog.models.Garment.count.field.name}"
        ),
        lookup_expr="gte",
    )

    class Meta:
        model = catalog.models.Product
        fields = {
            catalog.models.Product.price.field.name: ["gte", "lte"],
        }


class GarmentFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = catalog.models.Garment
        fields = {
            catalog.models.Garment.count.field.name: ["gte", "lte"],
        }


class OrderFilter(django_filters.rest_framework.FilterSet):
    class Meta:
        model = catalog.models.Order
        fields = [catalog.models.Order.status.field.name]
