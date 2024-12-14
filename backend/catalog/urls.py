import django.contrib.auth.forms
import django.contrib.auth.views
import django.urls

import catalog.views


app_name = "users"


urlpatterns = [
    django.urls.path(
        "items/",
        catalog.views.ItemListView.as_view(),
        name="items",
    ),
    django.urls.path(
        "constructor-product/create/",
        catalog.views.ConstructorProductCreateView.as_view(),
        name="constructor-product-create",
    ),
]
