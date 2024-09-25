from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    title = models.CharField(max_length=255,null=True)
    author = models.CharField(max_length=255, null=True)
    description = models.TextField(null=True)
    year  = models.CharField(max_length=4, default='0000')
    isbn = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='static/bookImages/', null=True)
    ebook = models.FileField(upload_to='ebook/', null=True, blank=True)
    def __str__(self):
        return self.title


class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    book = models.ForeignKey(Book, on_delete=models.CASCADE) 
    added_on = models.DateTimeField(auto_now_add=True)  

    class Meta:
        unique_together = ['user', 'book'] 

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"










