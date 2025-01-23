import django_elasticsearch_dsl
import django_elasticsearch_dsl.registries

import support.models


@django_elasticsearch_dsl.registries.registry.register_document
class MessageDocument(django_elasticsearch_dsl.Document):
    user_id = django_elasticsearch_dsl.fields.IntegerField()

    class Index:
        name = "messages"
        settings = {
            "number_of_shards": 2,
            "number_of_replicas": 1,
        }
        ignore = True

    class Django:
        model = support.models.Message
        fields = [
            support.models.Message.id.field.name,
            support.models.Message.created_at.field.name,
        ]
