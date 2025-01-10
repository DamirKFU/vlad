import rest_framework.pagination


class OrderStaffPagination(rest_framework.pagination.PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 10
