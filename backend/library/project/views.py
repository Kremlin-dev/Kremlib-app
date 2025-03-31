import os
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status, viewsets, pagination
from .auth import logout, invalidate_all_tokens
from rest_framework.decorators import api_view, permission_classes, authentication_classes, action
from django.http import HttpResponse
from .models import (
    Book, Collection, UserProfile, Rating, ReadingProgress, 
    Comment, Category, BookContent
)
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import (
    BookSerializer, CollectionSerializer, UserSerializer, CategorySerializer,
    RatingSerializer, ReadingProgressSerializer, CommentSerializer,
    UserProfileSerializer, BookContentSerializer, UserAnalyticsSerializer
)
from rest_framework.response import Response
from rest_framework import filters
from .filters import BookFilter
from django.db.models import Q, Count, Avg
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

class CursorPagination(pagination.CursorPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = '-uploaded_on'  # Default ordering by most recent
    cursor_query_param = 'cursor'  # The query parameter to use for the cursor

# Authentication Views
@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    from .utils import standard_response
    
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return standard_response(
            data={
                "refresh": str(refresh),
                "access": str(access),
                "username": user.username,
                "user_id": user.id
            },
            message="Signup was successful",
            status_code=status.HTTP_201_CREATED
        )
    return standard_response(
        message="User data could not be validated", 
        errors=serializer.errors, 
        status_code=status.HTTP_400_BAD_REQUEST
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    from .utils import standard_response
    
    serializer = TokenObtainPairSerializer(data=request.data)

    if serializer.is_valid():
        tokens = serializer.validated_data
        user = User.objects.get(username=request.data['username'])

        refresh = tokens['refresh']
        access = tokens['access']

        return standard_response(
            data={
                "refresh": str(refresh),
                "access": str(access),
                "username": user.username,
                "user_id": user.id
            },
            message="Login was successful"
        )
    return standard_response(
        message="Invalid credentials", 
        status_code=status.HTTP_401_UNAUTHORIZED
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def request_password_reset(request):
    """
    Request a password reset link to be sent to the user's email
    """
    email = request.data.get('email', '')
    from .utils import standard_response
    
    if not email:
        return standard_response(
            message="Email is required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
        # Generate a token for password reset
        token = RefreshToken.for_user(user)
        
        # In a real application, send an email with a link containing the token
        # For now, we'll just return the token in the response for testing purposes
        reset_link = f"http://localhost:3000/reset-password/{user.id}/{token}"
        
        # Here you would typically send an email with the reset link
        # send_mail(...)
        
        return standard_response(
            data={
                "reset_link": reset_link  # Remove this in production, just for testing
            },
            message="Password reset link has been sent to your email"
        )
    except User.DoesNotExist:
        # For security reasons, don't reveal that the email doesn't exist
        return standard_response(
            message="If this email exists in our system, a password reset link has been sent"
        )

@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password(request):
    """
    Reset the user's password using the token sent to their email
    """
    from .utils import standard_response
    
    user_id = request.data.get('user_id')
    token = request.data.get('token')
    new_password = request.data.get('new_password')
    
    if not all([user_id, token, new_password]):
        return standard_response(
            message="User ID, token, and new password are required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        
        # Verify the token (in a real app, you'd use a proper token validation)
        # This is a simplified version for demonstration
        try:
            # Attempt to verify the token
            # In a real app, you'd use a proper token validation mechanism
            # Here we're just checking if it's a valid JWT token format
            token_obj = RefreshToken(token)
            
            # Set the new password
            user.set_password(new_password)
            user.save()
            
            return standard_response(
                message="Password has been reset successfully"
            )
        except Exception as e:
            return standard_response(
                message="Invalid or expired token",
                status_code=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return standard_response(
            message="User not found",
            status_code=status.HTTP_404_NOT_FOUND
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """
    Change password for authenticated user
    """
    from .utils import standard_response
    
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')
    
    if not all([current_password, new_password]):
        return standard_response(
            message="Current password and new password are required",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if current password is correct
    if not user.check_password(current_password):
        return standard_response(
            message="Current password is incorrect",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    # Set new password
    user.set_password(new_password)
    user.save()
    
    return standard_response(
        message="Password changed successfully"
    )

# Import custom permissions and response utils
from .permissions import IsBookOwnerOrReadOnly, IsAdminOrReadOnly
from .utils import standard_response, paginated_response
from .cache_utils import cache_result, cache_view_method, invalidate_model_cache
from django.db.models import Prefetch

# Book Views
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = StandardResultsSetPagination  # Default pagination
    parser_classes = [MultiPartParser, FormParser]
    filterset_class = BookFilter
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'popular', 'search', 'by_category', 'preview', 'similar_books']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsBookOwnerOrReadOnly]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @cache_result(timeout=60*5)  # Cache for 5 minutes
    def get_queryset(self):
        # Start with optimized query using select_related for foreign keys
        queryset = Book.objects.select_related('uploaded_by').all()
        
        # Add prefetch_related for related collections to reduce queries
        queryset = queryset.prefetch_related(
            'favorites',  # Use the favorites M2M field instead of 'collections'
            Prefetch('ratings', queryset=Rating.objects.select_related('user'))
        )
        
        if self.action == 'list':
            # For public listing, only show public books
            if not self.request.user.is_authenticated:
                queryset = queryset.filter(is_public=True)
            # For authenticated users, show public books and their own private books
            else:
                queryset = queryset.filter(Q(is_public=True) | Q(uploaded_by=self.request.user))
                
        return queryset
        
    def perform_create(self, serializer):
        # Save the book and associate with current user
        instance = serializer.save(uploaded_by=self.request.user)
        # Invalidate cache after creating a new book
        invalidate_model_cache('Book')
        return instance
        
    def perform_update(self, serializer):
        # Save the updated book
        instance = serializer.save()
        # Invalidate cache for this specific book
        invalidate_model_cache('Book', instance.id)
        return instance
        
    def perform_destroy(self, instance):
        # Invalidate cache before deleting
        invalidate_model_cache('Book', instance.id)
        instance.delete()
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        instance.view_count += 1
        instance.save()
        serializer = self.get_serializer(instance, context={'request': request})
        return standard_response(
            data=serializer.data,
            message=f"Book '{instance.title}' details retrieved successfully"
        )
    
    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
        
    def create(self, request, *args, **kwargs):
        """
        Custom create method to handle file uploads
        """
        # Extract data from request
        data = request.data.copy()
        
        # Create serializer with data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        
        return standard_response(
            data={"book": serializer.data},
            message="Book uploaded successfully",
            status_code=status.HTTP_201_CREATED,
            headers=headers
        )
        
    def update(self, request, *args, **kwargs):
        """
        Custom update method to handle file uploads
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Extract data from request
        data = request.data.copy()
        
        # Create serializer with data
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({"message": "Book updated successfully", "book": serializer.data})
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        # Get popular books based on view count, download count, and ratings
        queryset = Book.objects.filter(is_public=True)
        queryset = queryset.annotate(
            avg_rating=Avg('ratings__rating'),
            total_activity=Count('ratings') + Count('comments') + models.F('view_count') + models.F('download_count')
        ).order_by('-total_activity', '-avg_rating', '-view_count')[:12]
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """
        Get personalized book recommendations based on user's reading history and ratings
        """
        if not request.user.is_authenticated:
            # For non-authenticated users, return popular books
            return self.popular(request)
            
        # Get user's reading history
        user_progress = ReadingProgress.objects.filter(user=request.user).select_related('book')
        read_book_ids = [progress.book.id for progress in user_progress]
        
        # Get user's ratings
        user_ratings = Rating.objects.filter(user=request.user).select_related('book')
        rated_books = {rating.book.id: rating.rating for rating in user_ratings}
        
        # Get categories of books the user has read or rated highly (4-5 stars)
        preferred_categories = set()
        for progress in user_progress:
            if progress.book.id in rated_books and rated_books[progress.book.id] >= 4:
                preferred_categories.add(progress.book.category)
            elif progress.completed:
                # If they completed a book, they probably liked it
                preferred_categories.add(progress.book.category)
                
        # If we don't have enough data, add some popular categories
        if len(preferred_categories) < 2:
            # Get most popular categories based on view counts
            popular_categories = Book.objects.filter(is_public=True)\
                .values('category')\
                .annotate(total_views=models.Sum('view_count'))\
                .order_by('-total_views')\
                .values_list('category', flat=True)[:3]
            preferred_categories.update(popular_categories)
            
        # Get books in preferred categories that the user hasn't read yet
        category_recommendations = Book.objects.filter(
            category__in=preferred_categories,
            is_public=True
        ).exclude(id__in=read_book_ids).order_by('-view_count')[:5]
        
        # Get books that are similar to highly rated books (same author or similar titles)
        similar_recommendations = []
        for book_id, rating in rated_books.items():
            if rating >= 4:
                # User liked this book, find similar ones
                book = Book.objects.get(id=book_id)
                similar_books = Book.objects.filter(
                    Q(author=book.author) | Q(title__icontains=book.title.split()[0] if book.title and book.title.split() else ''),
                    is_public=True
                ).exclude(id__in=read_book_ids + [book_id])
                similar_recommendations.extend(list(similar_books[:2]))
                
        # Combine recommendations, removing duplicates
        all_recommendations = list(category_recommendations)
        for book in similar_recommendations:
            if book not in all_recommendations:
                all_recommendations.append(book)
                if len(all_recommendations) >= 10:
                    break
                    
        # If we still don't have enough recommendations, add some popular books
        if len(all_recommendations) < 5:
            popular_books = Book.objects.filter(is_public=True)\
                .exclude(id__in=read_book_ids)\
                .exclude(id__in=[b.id for b in all_recommendations])\
                .order_by('-view_count')[:5]
            all_recommendations.extend(list(popular_books))
            
        serializer = self.get_serializer(all_recommendations, many=True, context={'request': request})
        return standard_response(
            data={
                'recommendations': serializer.data,
                'based_on': {
                    'reading_history': len(read_book_ids),
                    'ratings': len(rated_books),
                    'preferred_categories': list(preferred_categories)
                }
            },
            message='Personalized book recommendations generated successfully'
        )
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({"message": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) | 
            Q(description__icontains=query) | 
            Q(isbn__icontains=query),
            is_public=True
        )
        
    @action(detail=True, methods=['get'])
    def similar_books(self, request, pk=None):
        """
        Get books similar to the current book (same author, category, or related content)
        """
        book = self.get_object()
        
        # Find books by the same author
        same_author = Book.objects.filter(
            author=book.author,
            is_public=True
        ).exclude(id=book.id).order_by('-view_count')[:3]
        
        # Find books in the same category
        same_category = Book.objects.filter(
            category=book.category,
            is_public=True
        ).exclude(id=book.id).exclude(id__in=[b.id for b in same_author]).order_by('-view_count')[:3]
        
        # Find books with similar titles or descriptions (basic text similarity)
        title_words = [word for word in book.title.split() if len(word) > 3] if book.title else []
        if title_words:
            similar_title_query = Q()
            for word in title_words:
                similar_title_query |= Q(title__icontains=word)
                
            similar_title = Book.objects.filter(
                similar_title_query,
                is_public=True
            ).exclude(id=book.id)\
            .exclude(id__in=[b.id for b in list(same_author) + list(same_category)])\
            .order_by('-view_count')[:2]
        else:
            similar_title = []
            
        # Combine all similar books
        all_similar = list(same_author) + list(same_category) + list(similar_title)
        
        # If the user is authenticated, we can use their ratings to improve recommendations
        if request.user.is_authenticated:
            # Get books that users who read this book also rated highly
            users_who_read = ReadingProgress.objects.filter(book=book).values_list('user', flat=True)
            if users_who_read:
                other_books_read = ReadingProgress.objects.filter(
                    user__in=users_who_read
                ).exclude(book=book).values_list('book', flat=True)
                
                if other_books_read:
                    also_read = Book.objects.filter(
                        id__in=other_books_read,
                        is_public=True
                    ).exclude(id__in=[b.id for b in all_similar])\
                    .annotate(read_count=Count('id'))\
                    .order_by('-read_count')[:2]
                    
                    all_similar.extend(list(also_read))
        
        serializer = self.get_serializer(all_similar, many=True, context={'request': request})
        return standard_response(
            data={
                'book': book.title,
                'similar_books': serializer.data
            },
            message=f'Found {len(all_similar)} books similar to "{book.title}"'
        )
        
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download a book and increment its download count
        """
        book = self.get_object()
        
        # Check if the book has an ebook file
        if not book.ebook:
            return standard_response(
                message='No downloadable file available for this book',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        # Increment download count
        book.download_count += 1
        book.save()
        
        # Get the file path
        file_path = book.ebook.path
        
        # Return the file for download
        try:
            with open(file_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename={book.ebook.name.split("/")[-1]}'
                return response
        except Exception as e:
            return Response({
                'message': f'Error downloading file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    @action(detail=True, methods=['get'])
    def read(self, request, pk=None):
        """
        Read a book online and update reading progress
        """
        book = self.get_object()
        
        # Check if the book has an ebook file
        if not book.ebook:
            return Response({
                'message': 'No readable content available for this book'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Increment view count if this is a new session
        book.view_count += 1
        book.save()
        
        # Get or create reading progress for authenticated users
        if request.user.is_authenticated:
            reading_progress, created = ReadingProgress.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={
                    'current_page': 0,
                    'total_pages': 100  # This would be calculated based on the actual book content
                }
            )
            
        # Return book content for reading
        try:
            with open(book.ebook.path, 'rb') as file:
                content = file.read()
                
                # Determine content type based on file extension
                file_ext = book.ebook.name.split('.')[-1].lower()
                if file_ext == 'pdf':
                    content_type = 'application/pdf'
                elif file_ext in ['txt', 'text']:
                    content_type = 'text/plain'
                elif file_ext in ['epub', 'mobi']:
                    content_type = 'application/octet-stream'
                else:
                    content_type = 'application/octet-stream'
                
                response = HttpResponse(content, content_type=content_type)
                response['Content-Disposition'] = f'inline; filename={book.ebook.name.split("/")[-1]}'
                return response
        except Exception as e:
            return Response({
                'message': f'Error reading file: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Get a preview of a book (first few pages) without incrementing view count
        """
        book = self.get_object()
        
        # Check if the book has an ebook file
        if not book.ebook:
            return Response({
                'message': 'No preview available for this book'
            }, status=status.HTTP_404_NOT_FOUND)
            
        try:
            # For PDF files, we would extract just the first few pages
            # For text files, we can get the first few lines
            # This is a simplified version that works for text-based files
            with open(book.ebook.path, 'rb') as file:
                file_ext = book.ebook.name.split('.')[-1].lower()
                
                if file_ext == 'pdf':
                    # For PDF files, we need to use PyPDF2 to extract the first few pages
                    try:
                        from PyPDF2 import PdfReader
                        reader = PdfReader(file)
                        
                        # Get table of contents if available
                        toc = []
                        if hasattr(reader, 'outline') and reader.outline:
                            # This is a simplified TOC extraction
                            # A real implementation would recursively process the outline
                            for item in reader.outline:
                                if isinstance(item, dict) and '/Title' in item:
                                    toc.append(item['/Title'])
                        
                        # Extract text from first 3 pages or 10% of the book, whichever is less
                        preview_pages = min(3, len(reader.pages))
                        preview_text = ''
                        for i in range(preview_pages):
                            page = reader.pages[i]
                            preview_text += page.extract_text()
                            if len(preview_text) > 5000:  # Limit preview size
                                preview_text = preview_text[:5000] + '...'
                                break
                        
                        return Response({
                            'title': book.title,
                            'author': book.author,
                            'description': book.description,
                            'category': book.category,
                            'year': book.year,
                            'isbn': book.isbn,
                            'total_pages': len(reader.pages),
                            'table_of_contents': toc,
                            'preview_text': preview_text,
                            'preview_type': 'text'
                        })
                    except ImportError:
                        # If PyPDF2 is not available, return metadata only
                        return Response({
                            'message': 'PDF preview requires PyPDF2 library',
                            'title': book.title,
                            'author': book.author,
                            'description': book.description,
                            'category': book.category,
                            'year': book.year,
                            'isbn': book.isbn
                        })
                        
                elif file_ext in ['txt', 'text']:
                    # For text files, read the first 5000 characters
                    content = file.read(5000).decode('utf-8', errors='replace')
                    if file.read(1):  # Check if there's more content
                        content += '...'
                    
                    # Simple TOC generation for text files (chapter detection)
                    lines = content.split('\n')
                    toc = []
                    for line in lines:
                        if (line.lower().startswith('chapter') or 
                            (line.strip() and line.strip().isupper() and len(line.strip()) > 5)):
                            toc.append(line.strip())
                            if len(toc) >= 10:  # Limit TOC entries
                                break
                    
                    return Response({
                        'title': book.title,
                        'author': book.author,
                        'description': book.description,
                        'category': book.category,
                        'year': book.year,
                        'isbn': book.isbn,
                        'table_of_contents': toc,
                        'preview_text': content,
                        'preview_type': 'text'
                    })
                    
                elif file_ext in ['epub', 'mobi']:
                    # For EPUB/MOBI, we would need specialized libraries
                    # This is a placeholder for future implementation
                    return Response({
                        'message': f'{file_ext.upper()} preview not fully implemented yet',
                        'title': book.title,
                        'author': book.author,
                        'description': book.description,
                        'category': book.category,
                        'year': book.year,
                        'isbn': book.isbn
                    })
                    
                else:
                    # For other file types, just return metadata
                    return Response({
                        'title': book.title,
                        'author': book.author,
                        'description': book.description,
                        'category': book.category,
                        'year': book.year,
                        'isbn': book.isbn,
                        'message': f'Preview not available for {file_ext.upper()} files'
                    })
                    
            # End of with block
        except Exception as e:
            return Response({
                'message': f'Error generating preview: {str(e)}',
                'title': book.title,
                'author': book.author,
                'description': book.description
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Get or create reading progress for authenticated users
        if request.user.is_authenticated:
            reading_progress, created = ReadingProgress.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={
                    'current_page': 0,
                    'total_pages': 100  # This would be calculated based on the actual book content
                }
            )
            
            # Return book content with reading progress
            try:
                # For PDF files, we would need to use a library like PyPDF2 to extract content
                # For text files, we can simply read the content
                # This is a simplified version that works for text-based files
                with open(book.ebook.path, 'rb') as file:
                    content = file.read()
                    
                    # Determine content type based on file extension
                    file_ext = book.ebook.name.split('.')[-1].lower()
                    if file_ext == 'pdf':
                        content_type = 'application/pdf'
                    elif file_ext in ['txt', 'text']:
                        content_type = 'text/plain'
                    elif file_ext in ['epub', 'mobi']:
                        # For EPUB/MOBI, we would need special handling
                        # This is just a placeholder
                        content_type = 'application/octet-stream'
                    else:
                        content_type = 'application/octet-stream'
                    
                    response = HttpResponse(content, content_type=content_type)
                    
                    # For inline display in browser
                    response['Content-Disposition'] = f'inline; filename={book.ebook.name.split("/")[-1]}'
                    
                    return response
            except Exception as e:
                return Response({
                    'message': f'Error reading file: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            # For unauthenticated users, just serve the file without tracking progress
            try:
                with open(book.ebook.path, 'rb') as file:
                    content = file.read()
                    
                    # Determine content type based on file extension
                    file_ext = book.ebook.name.split('.')[-1].lower()
                    if file_ext == 'pdf':
                        content_type = 'application/pdf'
                    elif file_ext in ['txt', 'text']:
                        content_type = 'text/plain'
                    else:
                        content_type = 'application/octet-stream'
                    
                    response = HttpResponse(content, content_type=content_type)
                    response['Content-Disposition'] = f'inline; filename={book.ebook.name.split("/")[-1]}'
                    return response
            except Exception as e:
                return Response({
                    'message': f'Error reading file: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Apply filters if provided
        category = request.query_params.get('category', None)
        year = request.query_params.get('year', None)
        
        if category:
            queryset = queryset.filter(category=category)
        
        if year:
            queryset = queryset.filter(year=year)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category = request.query_params.get('category', None)
        if not category:
            return Response({"message": "Category parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        queryset = Book.objects.filter(category=category, is_public=True)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        
    @action(detail=False, methods=['get'])
    def infinite_scroll(self, request):
        """
        Endpoint optimized for infinite scrolling with cursor-based pagination
        """
        # Use cursor pagination for this endpoint
        self.pagination_class = CursorPagination
        
        # Get query parameters for filtering
        category = request.query_params.get('category', None)
        search_query = request.query_params.get('search', None)
        sort_by = request.query_params.get('sort_by', '-uploaded_on')  # Default sort by newest
        
        # Update the ordering based on sort parameter
        if hasattr(self.pagination_class, 'ordering'):
            if sort_by == 'popular':
                self.pagination_class.ordering = '-view_count'
            elif sort_by == 'downloads':
                self.pagination_class.ordering = '-download_count'
            elif sort_by == 'title':
                self.pagination_class.ordering = 'title'
            elif sort_by == 'author':
                self.pagination_class.ordering = 'author'
            else:
                self.pagination_class.ordering = sort_by
        
        # Start with all public books
        queryset = Book.objects.filter(is_public=True)
        
        # Apply category filter if provided
        if category:
            queryset = queryset.filter(category=category)
            
        # Apply search filter if provided
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(isbn__icontains=search_query)
            )
            
        # Paginate the results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True, context={'request': request})
            pagination_data = {
                'results': serializer.data,
                'next': self.paginator.get_next_link(),
                'previous': self.paginator.get_previous_link()
            }
            
            # Add filtering info to response
            filter_info = {
                'category': category,
                'search_query': search_query,
                'sort_by': sort_by
            }
            
            return standard_response(
                data=pagination_data,
                message='Books retrieved successfully',
                filters=filter_info
            )
            
        # If pagination is disabled, return all results
        serializer = self.get_serializer(queryset, many=True, context={'request': request})
        return standard_response(
            data={'results': serializer.data},
            message='Books retrieved successfully'
        )
    
    # Note: The main download method is already implemented as a GET endpoint above
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        book = self.get_object()
        user = request.user
        
        # Check if book is already in user's collection
        collection_exists = Collection.objects.filter(user=user, book=book).exists()
        
        if collection_exists:
            # Remove from favorites
            Collection.objects.filter(user=user, book=book).delete()
            return Response({"message": "Book removed from favorites"})
        else:
            # Add to favorites
            Collection.objects.create(user=user, book=book)
            return Response({"message": "Book added to favorites"})

# User Dashboard and Profile Views
class UserDashboardView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        user = request.user
        
        # Get user's uploaded books
        uploaded_books = Book.objects.filter(uploaded_by=user)
        uploaded_books_serializer = BookSerializer(uploaded_books, many=True, context={'request': request})
        
        # Get user's favorite books
        favorite_books = Book.objects.filter(collection__user=user)
        favorite_books_serializer = BookSerializer(favorite_books, many=True, context={'request': request})
        
        # Get user's reading progress
        reading_progress = ReadingProgress.objects.filter(user=user)
        reading_progress_serializer = ReadingProgressSerializer(reading_progress, many=True)
        
        # Get user's analytics
        analytics_serializer = UserAnalyticsSerializer(user)
        
        return standard_response(
            data={
                'uploaded_books': uploaded_books_serializer.data,
                'favorite_books': favorite_books_serializer.data,
                'reading_progress': reading_progress_serializer.data,
                'analytics': analytics_serializer.data
            },
            message='User dashboard data retrieved successfully'
        )

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    authentication_classes = [JWTAuthentication]
    parser_classes = [MultiPartParser, FormParser]  # Add parsers for file uploads
    
    def get_permissions(self):
        if self.action in ['retrieve', 'update', 'partial_update', 'destroy', 'upload_profile_picture', 'update_profile', 'delete_account']:
            permission_classes = [IsAuthenticated, IsProfileOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return UserProfile.objects.none()
            
        return UserProfile.objects.filter(user=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        instance = get_object_or_404(UserProfile, user=request.user)
        serializer = self.get_serializer(instance)
        return standard_response(
            data=serializer.data,
            message='User profile retrieved successfully'
        )
    
    def update(self, request, *args, **kwargs):
        instance = get_object_or_404(UserProfile, user=request.user)
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='upload-profile-picture')
    def upload_profile_picture(self, request):
        """
        Upload a profile picture for the current user
        """
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            
            # Check if profile picture was provided
            if 'profile_picture' not in request.FILES:
                return Response({
                    'message': 'No profile picture provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete old profile picture if it exists
            if profile.profile_picture:
                try:
                    if os.path.isfile(profile.profile_picture.path):
                        os.remove(profile.profile_picture.path)
                except Exception as e:
                    # Just log the error but continue with the update
                    print(f"Error removing old profile picture: {str(e)}")
            
            # Update profile picture
            profile.profile_picture = request.FILES['profile_picture']
            profile.save()
            
            return Response({
                'message': 'Profile picture updated successfully',
                'profile_picture_url': request.build_absolute_uri(profile.profile_picture.url)
            })
        except Exception as e:
            return Response({
                'message': f'Error uploading profile picture: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['put'], url_path='update-profile')
    def update_profile(self, request):
        """
        Update user profile information
        """
        try:
            profile = get_object_or_404(UserProfile, user=request.user)
            user = request.user
            
            # Update User model fields
            if 'email' in request.data:
                user.email = request.data['email']
            if 'username' in request.data:
                # Check if username is already taken
                if User.objects.filter(username=request.data['username']).exclude(id=user.id).exists():
                    return Response({
                        'message': 'Username is already taken'
                    }, status=status.HTTP_400_BAD_REQUEST)
                user.username = request.data['username']
            user.save()
            
            # Update UserProfile model fields
            if 'first_name' in request.data:
                profile.first_name = request.data['first_name']
            if 'last_name' in request.data:
                profile.last_name = request.data['last_name']
            if 'bio' in request.data:
                profile.bio = request.data['bio']
            profile.save()
            
            # Return updated profile data
            serializer = self.get_serializer(profile)
            return Response({
                'message': 'Profile updated successfully',
                'profile': serializer.data
            })
        except Exception as e:
            return Response({
                'message': f'Error updating profile: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['delete'], url_path='delete-account')
    def delete_account(self, request):
        """
        Delete user account and all associated data
        """
        try:
            user = request.user
            profile = get_object_or_404(UserProfile, user=user)
            
            # Verify password for security
            password = request.data.get('password')
            if not password or not user.check_password(password):
                return Response({
                    'message': 'Current password is required to delete your account'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Delete profile picture if it exists
            if profile.profile_picture:
                try:
                    if os.path.isfile(profile.profile_picture.path):
                        os.remove(profile.profile_picture.path)
                except Exception as e:
                    # Just log the error but continue with deletion
                    print(f"Error removing profile picture during account deletion: {str(e)}")
            
            # Delete user account (this will cascade delete all related objects)
            user.delete()
            
            return Response({
                'message': 'Your account has been successfully deleted'
            })
        except Exception as e:
            return Response({
                'message': f'Error deleting account: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Collection (Favorites) Views
class CollectionViewSet(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Collection.objects.none()
            
        return Collection.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Rating Views
class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Rating.objects.none()
            
        book_id = self.request.query_params.get('book_id', None)
        if book_id:
            return Rating.objects.filter(book_id=book_id)
        return Rating.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Check if user already rated this book
        book_id = self.request.data.get('book')
        existing_rating = Rating.objects.filter(user=self.request.user, book_id=book_id).first()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = self.request.data.get('rating')
            existing_rating.review = self.request.data.get('review', '')
            existing_rating.save()
            serializer = self.get_serializer(existing_rating)
            return Response(serializer.data)
        
        serializer.save(user=self.request.user)

# Comment Views
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()
            
        book_id = self.request.query_params.get('book_id', None)
        if book_id:
            return Comment.objects.filter(book_id=book_id)
        return Comment.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# Reading Progress Views
class ReadingProgressViewSet(viewsets.ModelViewSet):
    queryset = ReadingProgress.objects.all()
    serializer_class = ReadingProgressSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return ReadingProgress.objects.none()
            
        return ReadingProgress.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        # Check if progress already exists for this book
        book_id = self.request.data.get('book')
        existing_progress = ReadingProgress.objects.filter(user=self.request.user, book_id=book_id).first()
        
        if existing_progress:
            # Update existing progress
            existing_progress.current_page = self.request.data.get('current_page', existing_progress.current_page)
            existing_progress.total_pages = self.request.data.get('total_pages', existing_progress.total_pages)
            existing_progress.completed = self.request.data.get('completed', existing_progress.completed)
            existing_progress.save()
            serializer = self.get_serializer(existing_progress)
            return Response(serializer.data)
        
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def get_last_position(self, request):
        """
        Get the last reading position for a specific book
        """
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response({"message": "Book ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            progress = ReadingProgress.objects.get(user=request.user, book_id=book_id)
            serializer = self.get_serializer(progress)
            return Response(serializer.data)
        except ReadingProgress.DoesNotExist:
            return Response({
                "message": "No reading progress found for this book",
                "current_page": 0,
                "total_pages": 0,
                "completed": False
            })
    
    @action(detail=False, methods=['post'])
    def update_position(self, request):
        """
        Update the reading position for a book
        """
        book_id = request.data.get('book_id')
        current_page = request.data.get('current_page')
        total_pages = request.data.get('total_pages')
        completed = request.data.get('completed', False)
        
        if not book_id or current_page is None:
            return Response({"message": "Book ID and current page are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            book = Book.objects.get(id=book_id)
            progress, created = ReadingProgress.objects.get_or_create(
                user=request.user,
                book=book,
                defaults={
                    'current_page': current_page,
                    'total_pages': total_pages or 100,
                    'completed': completed
                }
            )
            
            if not created:
                progress.current_page = current_page
                if total_pages is not None:
                    progress.total_pages = total_pages
                progress.completed = completed
                progress.save()
            
            return Response({
                "message": "Reading position updated successfully",
                "progress": self.get_serializer(progress).data
            })
        except Book.DoesNotExist:
            return Response({"message": "Book not found"}, status=status.HTTP_404_NOT_FOUND)

# Category Views
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]

# Book Content Views (for writing books on the platform)
class BookContentViewSet(viewsets.ModelViewSet):
    queryset = BookContent.objects.all()
    serializer_class = BookContentSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_queryset(self):
        # Check if this is a schema request from Swagger
        if getattr(self, 'swagger_fake_view', False):
            return BookContent.objects.none()
            
        return BookContent.objects.filter(book__uploaded_by=self.request.user)
    
    def perform_create(self, serializer):
        book_id = self.request.data.get('book')
        book = get_object_or_404(Book, id=book_id, uploaded_by=self.request.user)
        serializer.save(book=book)

# Legacy Views - Keeping for backward compatibility
@api_view(["GET"])
@permission_classes([AllowAny])
def home(request):
    books = Book.objects.filter(is_public=True).order_by('-uploaded_on')[:20]
    serializer = BookSerializer(books, many=True, context={'request': request})
    if serializer.data:
        return Response(serializer.data)
    return Response({"message": "Books not found!"})
