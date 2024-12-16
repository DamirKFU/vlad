import django.contrib
import sorl.thumbnail.admin

import catalog.models


class ConstructorProductImageInline(
    sorl.thumbnail.admin.AdminImageMixin, django.contrib.admin.TabularInline
):
    fields = ["image", "image_tmb"]
    readonly_fields = ["image_tmb"]
    model = catalog.models.ConstructorProductImage


class ConstructorEmbroideryImageInline(
    sorl.thumbnail.admin.AdminImageMixin, django.contrib.admin.TabularInline
):
    fields = ["image"]
    model = catalog.models.ConstructorEmbroideryImage


@django.contrib.admin.register(catalog.models.Category)
class CategoryAdmin(django.contrib.admin.ModelAdmin):
    list_display = (catalog.models.Category.name.field.name,)


@django.contrib.admin.register(catalog.models.Color)
class ColorAdmin(django.contrib.admin.ModelAdmin):
    list_display = (catalog.models.Color.name.field.name,)


@django.contrib.admin.register(catalog.models.Item)
class TShirtAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        catalog.models.Item.id.field.name,
        catalog.models.Item.category.field.name,
        catalog.models.Item.color.field.name,
        catalog.models.Item.size.field.name,
        catalog.models.Item.count.field.name,
    )
    list_display_links = (catalog.models.Item.id.field.name,)


@django.contrib.admin.register(catalog.models.ConstructorProduct)
class ConstructorProductAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        catalog.models.ConstructorProduct.item.field.name,
        catalog.models.ConstructorProduct.status.field.name,
    )
    readonly_fields = (catalog.models.ConstructorProduct.user.field.name,)
    list_editable = (catalog.models.ConstructorProduct.status.field.name,)
    inlines = [
        ConstructorProductImageInline,
        ConstructorEmbroideryImageInline,
    ]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

        super().save_model(request, obj, form, change)
