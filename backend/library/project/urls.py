from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.userlogin, name = 'login'),
    path('signup/', views.signup, name = 'signup'),
   
]