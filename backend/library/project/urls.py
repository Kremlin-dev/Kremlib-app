from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login, name = 'login'),
    path('signup/', views.register, name = 'signup'),
    path('home/', views.home, name='home'),
    path('getbooks/', views.getallbooks, name='name'),
    path('uploadbook/',views.uploadbook, name='uploadbook'),
]