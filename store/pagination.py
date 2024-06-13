from rest_framework.pagination import PageNumberPagination

class CustomPagePagination(PageNumberPagination):
    page_size = 10