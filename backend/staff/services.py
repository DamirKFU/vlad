import catalog.models
import core.elasticsearch


class OrderLogService:
    def __init__(self, order_id, page_size, current_page):
        self.order_id = order_id
        self.page_size = page_size
        self.current_page = current_page
        self.es = core.elasticsearch.ElasticsearchClient.get_instance()

    def get_logs(self):
        result = self.es.search(
            index="django-orders-*",
            body=self._build_query(),
        )

        return self._process_results(result)

    def _build_query(self):
        return {
            "query": {
                "bool": {"must": [{"match": {"order_id": self.order_id}}]}
            },
            "sort": [{"@timestamp": {"order": "desc"}}],
            "size": self.page_size,
            "from": (self.current_page - 1) * self.page_size,
        }

    def _get_status_label(self, status):
        return catalog.models.OrderStatus._value2member_map_[status]._label_

    def _process_results(self, result):
        total = result["hits"]["total"]["value"]
        logs = []
        for hit in result["hits"]["hits"]:
            from_status = hit["_source"].get("from_status")
            to_status = hit["_source"].get("to_status")
            logs.append(
                {
                    "username": hit["_source"].get("username"),
                    "from_status": self._get_status_label(from_status),
                    "to_status": self._get_status_label(to_status),
                    "error_comment": hit["_source"].get("error_comment"),
                    "created_at": hit["_source"].get("@timestamp"),
                }
            )

        total_pages = (total + self.page_size - 1) // self.page_size

        return {
            "count": total,
            "total_pages": total_pages,
            "next": self.current_page < total_pages,
            "previous": self.current_page > 1,
            "results": logs,
        }
