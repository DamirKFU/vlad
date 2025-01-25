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
        "categories/",
        catalog.views.CategoryListView.as_view(),
        name="categories",
    ),
    django.urls.path(
        "colors/",
        catalog.views.ColorListView.as_view(),
        name="colors",
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
        "products/<int:pk>/",
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
        "cart/item/<int:pk>/",
        catalog.views.UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),
    django.urls.path(
        "orders/",
        catalog.views.OrderHistoryView.as_view(),
        name="order-history",
    ),
    django.urls.path(
        "orders/<int:pk>/",
        catalog.views.OrderDetailView.as_view(),
        name="order-detail",
    ),
]
