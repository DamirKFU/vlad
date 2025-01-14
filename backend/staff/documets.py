import elasticsearch_dsl


class OrderLogDocument(elasticsearch_dsl.Document):
    username = elasticsearch_dsl.Text()
    from_status = elasticsearch_dsl.Keyword()
    to_status = elasticsearch_dsl.Keyword()
    error_comment = elasticsearch_dsl.Text()
    created_at = elasticsearch_dsl.Date()

    @staticmethod
    def search_by_order_id(order_id, page_size, current_page):
        s = OrderLogDocument.search().query("match", order_id=order_id)
        s = s.sort({"@timestamp": {"order": "desc"}})
        start = page_size * (current_page - 1)
        end = start + page_size
        s = s[start:end]
        return s.execute()

    class Index:
        name = "django-orders-*"
