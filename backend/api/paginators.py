from recipes.constants import PAGE_LIMIT_SIZE
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Кастомная пагинация"""
    page_size_query_param = 'limit'
    page_size = PAGE_LIMIT_SIZE
