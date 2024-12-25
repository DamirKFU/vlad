import django.contrib.auth.forms
import django.contrib.auth.views
import django.urls

import catalog.views


app_name = "catalog"


urlpatterns = [
    django.urls.path(
        "garments/",
        catalog.views.GarmentListView.as_view(),
        name="garments",
    ),
    django.urls.path(
        "constructor-product/create/",
        catalog.views.ConstructorProductCreateView.as_view(),
        name="constructor-product-create",
    ),
    django.urls.path(
        "products/",
        catalog.views.ProductListView.as_view(),
        name="products",
    ),
    django.urls.path(
        "product/<int:product_id>/",
        catalog.views.ProductDetailView.as_view(),
        name="product-detail",
    ),
    django.urls.path(
        "cart/add/",
        catalog.views.AddToCartView.as_view(),
        name="cart-add",
    ),
    django.urls.path(
        "cart/",
        catalog.views.CartView.as_view(),
        name="cart",
    ),
    django.urls.path(
        "cart/item/<int:item_id>/",
        catalog.views.UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),
]
