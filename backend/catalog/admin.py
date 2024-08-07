from django.contrib import admin

import catalog.models


@admin.register(catalog.models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Category.name.field.name,)


@admin.register(catalog.models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Color.name.field.name,)


@admin.register(catalog.models.TShirt)
class TShirtAdmin(admin.ModelAdmin):
    list_display = (
        catalog.models.TShirt.id.field.name,
        catalog.models.TShirt.category.field.name,
        catalog.models.TShirt.color.field.name,
        catalog.models.TShirt.size.field.name,
        catalog.models.TShirt.count.field.name,
    )
    list_display_links = (catalog.models.TShirt.id.field.name,)
    readonly_fields = (catalog.models.TShirt.image_tmb.field_name,)


@admin.register(catalog.models.Embroidery)
class EmbroideryAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Embroidery.name.field.name,)
    list_display_links = (catalog.models.Embroidery.name.field.name,)
    readonly_fields = (catalog.models.TShirt.image_tmb.field_name,)
