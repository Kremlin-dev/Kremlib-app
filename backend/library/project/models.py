from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

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
    ]

    title = models.CharField(max_length=255, null=True)
    author = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    year = models.CharField(max_length=4, default='0000')
    isbn = models.CharField(max_length=255, unique=True, null = True)  
    image = models.ImageField(upload_to='static/bookImages/', null=True)
    ebook = models.FileField(upload_to='ebooks/', null=True, blank=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_books')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    is_public = models.BooleanField(default=True)  
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author})"

class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'book']

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"
