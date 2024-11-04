from django.contrib import admin
from django.contrib.auth.models import User
from project.models import Book, Collection

class adminsite(admin.AdminSite):
    site_header = "KREMLIB ADMIN PANNEL"
    site_title = 'KREMLIB'
    index_title = "kremlib-admin"

siteadmin = adminsite(name= 'siteadmin')

class BookPanel(admin.ModelAdmin):
    list_display= ("title", "author", "description", "year", "isbn", "image", "ebook","uploaded_by","category","is_public","uploaded_on")

class CollectionPanel(admin.ModelAdmin):
    list_display =("user", "book", "added_on")

class UserPanel(admin.ModelAdmin):
    list_display= ("username","email", "password")

siteadmin.register(Book, BookPanel)
siteadmin.register(Collection, CollectionPanel)
siteadmin.register(User, UserPanel)