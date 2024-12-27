import rest_framework.pagination
import rest_framework.response


class ProductPagination(rest_framework.pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10

    def get_paginated_response(self, data):
        return rest_framework.response.Response(
            {
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )


class OrderPagination(rest_framework.pagination.PageNumberPagination):
    page_size = 2
    page_size_query_param = "page_size"
    max_page_size = 10
