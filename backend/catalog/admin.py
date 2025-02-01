import django.contrib.admin
import sorl.thumbnail.admin

import catalog.models


class BaseImageInline(
    sorl.thumbnail.admin.AdminImageMixin, django.contrib.admin.TabularInline
):
    def has_change_permission(self, request, obj=None):
        return False


class ConstructorProductImageInline(BaseImageInline):
    fields = [
        catalog.models.ConstructorProductImage.image.field.name,
        catalog.models.ConstructorProductImage.image_tmb.field_name,
    ]
    readonly_fields = [
        catalog.models.ConstructorProductImage.image.field.name,
        catalog.models.ConstructorProductImage.image_tmb.field_name,
    ]
    model = catalog.models.ConstructorProductImage


class ConstructorEmbroideryImageInline(BaseImageInline):
    fields = [catalog.models.ConstructorEmbroideryImage.image.field.name]
    readonly_fields = [
        catalog.models.ConstructorEmbroideryImage.image.field.name,
    ]
    model = catalog.models.ConstructorEmbroideryImage


class ProductMainImageInline(BaseImageInline):
    fields = [
        catalog.models.ProductMainImage.image.field.name,
        catalog.models.ProductMainImage.image_tmb.field_name,
    ]
    readonly_fields = [
        catalog.models.ProductMainImage.image_tmb.field_name,
    ]
    model = catalog.models.ProductMainImage

    def has_change_permission(self, request, obj):
        return False


class ProductSecondaryImageInline(BaseImageInline):
    fields = [
        catalog.models.ProductSecondaryImage.image.field.name,
        catalog.models.ProductSecondaryImage.image_tmb.field_name,
    ]
    readonly_fields = [
        catalog.models.ProductSecondaryImage.image_tmb.field_name,
    ]
    model = catalog.models.ProductSecondaryImage


class ProductAdditionalImageInline(BaseImageInline):
    fields = [
        catalog.models.ProductAdditionalImage.image.field.name,
        catalog.models.ProductAdditionalImage.image_tmb.field_name,
        catalog.models.ProductAdditionalImage.color.field.name,
        catalog.models.ProductAdditionalImage.category.field.name,
    ]
    readonly_fields = [
        catalog.models.ProductAdditionalImage.image_tmb.field_name,
    ]
    model = catalog.models.ProductAdditionalImage
    extra = 1


@django.contrib.admin.register(catalog.models.Category)
class CategoryAdmin(django.contrib.admin.ModelAdmin):
    list_display = (catalog.models.Category.name.field.name,)


@django.contrib.admin.register(catalog.models.Color)
class ColorAdmin(django.contrib.admin.ModelAdmin):
    list_display = (catalog.models.Color.name.field.name,)


@django.contrib.admin.register(catalog.models.Garment)
class GarmentAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        catalog.models.Garment.id.field.name,
        catalog.models.Garment.category.field.name,
        catalog.models.Garment.color.field.name,
        catalog.models.Garment.size.field.name,
        catalog.models.Garment.count.field.name,
    )
    list_display_links = (catalog.models.Garment.id.field.name,)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.method == "POST":
            qs = qs.select_for_update()
            return qs

        return qs


@django.contrib.admin.register(catalog.models.ConstructorProduct)
class ConstructorProductAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        catalog.models.ConstructorProduct.garment.field.name,
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


@django.contrib.admin.register(catalog.models.Product)
class ProductAdmin(django.contrib.admin.ModelAdmin):
    list_display = (
        catalog.models.Product.name.field.name,
        catalog.models.Product.price.field.name,
    )
    list_display_links = (catalog.models.Product.name.field.name,)
    filter_horizontal = (catalog.models.Product.garments.field.name,)
    inlines = [
        ProductMainImageInline,
        ProductSecondaryImageInline,
        ProductAdditionalImageInline,
    ]
