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
]
