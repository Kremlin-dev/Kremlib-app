from django.contrib import admin
from django.contrib.auth.models import User
from project.models import (
    Book, Collection, UserProfile, Rating, ReadingProgress, 
    Comment, Category, BookContent
)

class adminsite(admin.AdminSite):
    site_header = "KREMLIB ADMIN PANEL"
    site_title = 'KREMLIB'
    index_title = "kremlib-admin"

siteadmin = adminsite(name='siteadmin')

class BookPanel(admin.ModelAdmin):
    list_display = ("title", "author", "year", "isbn", "category", "uploaded_by", "is_public", "uploaded_on", "view_count", "download_count")
    list_filter = ("category", "is_public", "year")
    search_fields = ("title", "author", "isbn", "description")

class CollectionPanel(admin.ModelAdmin):
    list_display = ("user", "book", "added_on")
    list_filter = ("added_on",)
    search_fields = ("user__username", "book__title")

class UserPanel(admin.ModelAdmin):
    list_display = ("username", "email", "date_joined", "last_login", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "date_joined")
    search_fields = ("username", "email")

class UserProfilePanel(admin.ModelAdmin):
    list_display = ("user", "first_name", "last_name", "date_joined")
    search_fields = ("user__username", "first_name", "last_name")

class RatingPanel(admin.ModelAdmin):
    list_display = ("user", "book", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("user__username", "book__title", "review")

class ReadingProgressPanel(admin.ModelAdmin):
    list_display = ("user", "book", "current_page", "total_pages", "completed", "last_read")
    list_filter = ("completed", "last_read")
    search_fields = ("user__username", "book__title")

class CommentPanel(admin.ModelAdmin):
    list_display = ("user", "book", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = ("user__username", "book__title", "content")

class CategoryPanel(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

class BookContentPanel(admin.ModelAdmin):
    list_display = ("book", "created_at", "updated_at")
    search_fields = ("book__title",)

# Register models with the admin site
siteadmin.register(Book, BookPanel)
siteadmin.register(Collection, CollectionPanel)
siteadmin.register(User, UserPanel)
siteadmin.register(UserProfile, UserProfilePanel)
siteadmin.register(Rating, RatingPanel)
siteadmin.register(ReadingProgress, ReadingProgressPanel)
siteadmin.register(Comment, CommentPanel)
siteadmin.register(Category, CategoryPanel)
siteadmin.register(BookContent, BookContentPanel)