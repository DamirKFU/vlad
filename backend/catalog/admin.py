from django.contrib import admin

import catalog.models


@admin.register(catalog.models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Category.name.field.name,)


@admin.register(catalog.models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Color.name.field.name,)


@admin.register(catalog.models.Item)
class TShirtAdmin(admin.ModelAdmin):
    list_display = (
        catalog.models.Item.id.field.name,
        catalog.models.Item.category.field.name,
        catalog.models.Item.color.field.name,
        catalog.models.Item.size.field.name,
        catalog.models.Item.count.field.name,
    )
    list_display_links = (catalog.models.Item.id.field.name,)
