from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    last_logout = models.DateTimeField(null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    failed_login_attempts = models.PositiveIntegerField(default=0)
    last_failed_login = models.DateTimeField(null=True, blank=True)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"

class Book(models.Model):
    CATEGORY_CHOICES = [
        ('Novel', 'Novel'),
        ('Entertainment', 'Entertainment'),
        ('Education', 'Education'),
        ('Science', 'Science'),
        ('Biography', 'Biography'),
        ('History', 'History'),
        ('Fantasy', 'Fantasy'),
        ('Mystery', 'Mystery'),
        ('Romance', 'Romance'),
        ('Action', 'Action'),
        ('Adventure', 'Adventure'),
        ('African Tales', 'African Tales'),
        ('Religious', 'Religious'),
    ]

    title = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    year = models.CharField(max_length=4, default='0000')
    isbn = models.CharField(max_length=255, unique=True, null=True)  
    image = models.ImageField(upload_to='static/bookImages/', null=True, blank=True)
    ebook = models.FileField(upload_to='ebooks/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_books')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_public = models.BooleanField(default=True)  
    uploaded_on = models.DateTimeField(auto_now_add=True)
    favorites = models.ManyToManyField(User, through='Collection', related_name='favorite_books')
    view_count = models.PositiveIntegerField(default=0)
    download_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.title} by {self.author}"

class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'book']
        
    def __str__(self):
        return f"{self.user.username}'s rating for {self.book.title}: {self.rating}"

class ReadingProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reading_progress')
    current_page = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=0)
    last_read = models.DateTimeField(auto_now=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['user', 'book']
        
    def __str__(self):
        return f"{self.user.username}'s progress on {self.book.title}: {self.current_page}/{self.total_pages}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"

class BookContent(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='content')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Content for {self.book.title}"
