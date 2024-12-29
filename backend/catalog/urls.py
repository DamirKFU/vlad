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
        "cart/item/",
        catalog.views.UpdateCartItemView.as_view(),
        name="update-cart-item",
    ),
    django.urls.path(
        "order/create/",
        catalog.views.CreateOrderView.as_view(),
        name="create-order",
    ),
    django.urls.path(
        "orders/history/",
        catalog.views.OrderHistoryView.as_view(),
        name="order-history",
    ),
    django.urls.path(
        "orders/<int:order_id>/",
        catalog.views.OrderDetailView.as_view(),
        name="order-detail",
    ),
]
