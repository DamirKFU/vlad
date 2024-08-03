from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

import catalog.models


class TShirtMainImageInline(AdminImageMixin, admin.TabularInline):
    fields = ["image"]
    model = catalog.models.TShirtMainImage


class EmbroideryMainImageInline(AdminImageMixin, admin.TabularInline):
    fields = ["image"]
    model = catalog.models.EmbroideryMainImage


class EmbroiderySecondaryImageInline(AdminImageMixin, admin.TabularInline):
    fields = ["image"]
    model = catalog.models.EmbroiderySecondaryImage


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

    inlines = [
        TShirtMainImageInline,
    ]


@admin.register(catalog.models.Embroidery)
class EmbroideryAdmin(admin.ModelAdmin):
    list_display = (catalog.models.Embroidery.name.field.name,)
    list_display_links = (catalog.models.Embroidery.name.field.name,)

    inlines = [
        EmbroideryMainImageInline,
        EmbroiderySecondaryImageInline,
    ]
