from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class Pagination(PageNumberPagination):
    
    page_size = 100
    page_query_param = 'p'
    page_size_query_param = 'size'
    max_page_size = 1000000

    def get_paginated_response(self, data):
        # Calculate the total number of pages
        total_pages = self.page.paginator.num_pages

        # Generate the list of available page numbers
        pages_list = list(range(1, total_pages + 1))

        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link() is not None,
            'previous': self.get_previous_link() is not None,
            'pages': pages_list,  
            'results': data,
        })