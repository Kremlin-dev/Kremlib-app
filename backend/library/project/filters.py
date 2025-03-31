import django_filters
from django.db.models import Q
from .models import Book, Rating, Comment, ReadingProgress, Collection

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains', label='Search by title')
    author = django_filters.CharFilter(lookup_expr='icontains', label='Search by author')
    year = django_filters.CharFilter(lookup_expr='exact', label='Filter by year')
    isbn = django_filters.CharFilter(field_name='isbn', lookup_expr='icontains', label='Search by ISBN')
    category = django_filters.ChoiceFilter(choices=Book.CATEGORY_CHOICES, label='Filter by category')
    min_rating = django_filters.NumberFilter(method='filter_by_min_rating', label='Minimum rating')
    is_public = django_filters.BooleanFilter(label='Public books only')
    search = django_filters.CharFilter(method='filter_search', label='Search all fields')
    
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'isbn', 'category', 'is_public']
    
    def filter_by_min_rating(self, queryset, name, value):
        # Filter books with average rating >= value
        return queryset.filter(ratings__rating__gte=value).distinct()
    
    def filter_search(self, queryset, name, value):
        # Search across multiple fields
        return queryset.filter(
            Q(title__icontains=value) |
            Q(author__icontains=value) |
            Q(description__icontains=value) |
            Q(isbn__icontains=value)
        ).distinct()

class RatingFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(label='Filter by book ID')
    user = django_filters.NumberFilter(label='Filter by user ID')
    min_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte', label='Minimum rating')
    max_rating = django_filters.NumberFilter(field_name='rating', lookup_expr='lte', label='Maximum rating')
    
    class Meta:
        model = Rating
        fields = ['book', 'user', 'rating']

class CommentFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(label='Filter by book ID')
    user = django_filters.NumberFilter(label='Filter by user ID')
    
    class Meta:
        model = Comment
        fields = ['book', 'user']

class ReadingProgressFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(label='Filter by book ID')
    user = django_filters.NumberFilter(label='Filter by user ID')
    completed = django_filters.BooleanFilter(label='Completed books only')
    
    class Meta:
        model = ReadingProgress
        fields = ['book', 'user', 'completed']

class CollectionFilter(django_filters.FilterSet):
    book = django_filters.NumberFilter(label='Filter by book ID')
    user = django_filters.NumberFilter(label='Filter by user ID')
    
    class Meta:
        model = Collection
        fields = ['book', 'user']