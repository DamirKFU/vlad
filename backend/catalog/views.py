import collections

import rest_framework.permissions
import rest_framework.response
import rest_framework.views

import catalog.models


class ItemListView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        items = catalog.models.Item.objects.all_items()
        result = collections.defaultdict(lambda: collections.defaultdict(dict))
        category_name_key = (
            f"{catalog.models.Item.category.field.name}"
            f"__{catalog.models.Category.name.field.name}"
        )
        size_key = catalog.models.Item.size.field.name
        count_key = catalog.models.Item.count.field.name
        color_name_key = (
            f"{catalog.models.Item.color.field.name}"
            f"__{catalog.models.Color.name.field.name}"
        )
        color_color_key = (
            f"{catalog.models.Item.color.field.name}"
            f"__{catalog.models.Color.color.field.name}"
        )
        for item in items:
            category_name = item[category_name_key]
            size = item[size_key]
            color_name = item[color_name_key]
            count = item[count_key]
            hex_color = item[color_color_key]

            result[category_name][size][color_name] = {
                "count": count,
                "hex": hex_color,
            }

        return rest_framework.response.Response(result)
