import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Search by title')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Search by author')
    year = django_filters.NumberFilter(lookup_expr='exact', label='Filter by year')
    ISBN = django_filters.CharFilter(lookup_expr='icontains', label='Search by ISBN')

    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'ISBN'] 