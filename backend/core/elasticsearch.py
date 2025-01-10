import django.conf
import elasticsearch


class ElasticsearchClient:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = elasticsearch.Elasticsearch(
                [django.conf.settings.ELASTICSEARCH_HOST],
                basic_auth=(
                    django.conf.settings.ELASTICSEARCH_USER,
                    django.conf.settings.ELASTICSEARCH_PASSWORD,
                ),
                verify_certs=False,
            )

        return cls._instance
