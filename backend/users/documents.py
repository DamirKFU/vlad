import django_elasticsearch_dsl
import django_elasticsearch_dsl.registries

import users.models


@django_elasticsearch_dsl.registries.registry.register_document
class UserDocument(django_elasticsearch_dsl.Document):
    class Index:
        name = "users"
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
        }

    class Django:
        model = users.models.User
        fields = [
            users.models.User.id.field.name,
            users.models.User.username.field.name,
        ]
