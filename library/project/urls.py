from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name= 'home'),
    path('login/', views.userlogin, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
    path('userdash/', views.userdash, name = 'userdash'),
    path('bookdetails/<int:id>/', views.book_details, name ='book_details'),
]