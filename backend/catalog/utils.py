import collections

import catalog.models


def get_structured_garments(garments_data):
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

    for garment in garments_data:
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

    return result
