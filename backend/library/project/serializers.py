from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import (
    Book, Collection, UserProfile, Rating, ReadingProgress, 
    Comment, Category, BookContent
)

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile_picture', 'bio', 'date_joined']

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'username', 'content', 'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class RatingSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'username', 'rating', 'review', 'created_at', 'updated_at']
        read_only_fields = ['user']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class ReadingProgressSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ReadingProgress
        fields = ['id', 'book', 'book_title', 'current_page', 'total_pages', 'last_read', 'completed', 'progress_percentage']
        read_only_fields = ['user']
    
    def get_progress_percentage(self, obj):
        if obj.total_pages > 0:
            return round((obj.current_page / obj.total_pages) * 100, 2)
        return 0
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class BookContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookContent
        fields = ['id', 'content', 'created_at', 'updated_at']

class BookSerializer(serializers.ModelSerializer):
    uploader = serializers.CharField(source='uploaded_by.username', read_only=True)
    ratings_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    content = BookContentSerializer(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'year', 'isbn', 'ebook',
            'image', 'category', 'is_public', 'uploaded_on', 'uploader',
            'view_count', 'download_count', 'ratings_count', 'average_rating',
            'is_favorited', 'comments', 'content'
        ]
        read_only_fields = ['uploaded_by', 'view_count', 'download_count']
    
    def get_ratings_count(self, obj):
        return obj.ratings.count()
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings:
            return sum(r.rating for r in ratings) / len(ratings)
        return 0
    
    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Collection.objects.filter(user=request.user, book=obj).exists()
        return False
    
    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)

class CollectionSerializer(serializers.ModelSerializer):
    book_details = BookSerializer(source='book', read_only=True)
    
    class Meta:
        model = Collection
        fields = ['id', 'user', 'book', 'book_details', 'added_on']
        read_only_fields = ['user', 'added_on']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'profile']

    def create(self, validated_data):
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        
        # Create user profile
        UserProfile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name
        )
        
        return user

class UserAnalyticsSerializer(serializers.ModelSerializer):
    books_uploaded = serializers.SerializerMethodField()
    books_read = serializers.SerializerMethodField()
    books_in_progress = serializers.SerializerMethodField()
    favorite_books = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'books_uploaded', 'books_read', 'books_in_progress', 'favorite_books']
    
    def get_books_uploaded(self, obj):
        return obj.uploaded_books.count()
    
    def get_books_read(self, obj):
        return ReadingProgress.objects.filter(user=obj, completed=True).count()
    
    def get_books_in_progress(self, obj):
        return ReadingProgress.objects.filter(user=obj, completed=False).exclude(current_page=0).count()
    
    def get_favorite_books(self, obj):
        return obj.favorite_books.count()