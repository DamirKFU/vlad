import django_elasticsearch_dsl
import django_elasticsearch_dsl.registries

import users.models


@django_elasticsearch_dsl.registries.registry.register_document
class UserDocument(django_elasticsearch_dsl.Document):
    class Index:
        name = "users"

    class Django:
        model = users.models.User
        fields = [
            "id",
            "username",
        ]
