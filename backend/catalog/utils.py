import collections


def get_structured_images(product):
    result = collections.defaultdict(list)

    additional_images = product.additional_images.get_images_for_garments(
        product
    )

    for image in additional_images:
        result[image.color.name].append(image.get_image_330x440().url)

    return result
