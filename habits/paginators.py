from rest_framework.pagination import PageNumberPagination


class HabitsPaginator(PageNumberPagination):
    """Настраивает пагинацию для списка привычек (по 5 на странице)"""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
