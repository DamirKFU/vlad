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
]
