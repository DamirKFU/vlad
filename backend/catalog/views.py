import collections

import rest_framework.permissions
import rest_framework.response
import rest_framework.views

import catalog.models


class ItemListView(rest_framework.views.APIView):
    permission_classes = (rest_framework.permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        items = catalog.models.Item.objects.all()
        result = collections.defaultdict(lambda: collections.defaultdict(dict))

        for item in items:
            category_name = item.category.name
            size = item.size
            color_name = item.color.name
            count = item.count
            hex_color = item.color.color

            result[category_name][size][color_name] = {
                "count": count,
                "hex": hex_color,
            }

        return rest_framework.response.Response(result)
