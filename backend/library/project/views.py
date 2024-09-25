from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .models import Book, Collection
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
@api_view["GET"]
def get_allbooks(request):
    query = request.GET.get("query")
    search_by = request.GET.get("search_by")

    if not query and not search_by:
                books = Book.objects.all()[:10]

    else:
        if search_by == 'title':
            books = Book.objects.filter(title__icontains=query)

        elif search_by == 'author':
            books = Book.objects.filter(author__icontains=query)

        elif search_by == 'isbn':
            books = Book.objects.filter(isbn__icontains=query)

    context = {
            'books':books,

        }
    template = loader.get_template('home.html')
    return HttpResponse(template.render(context, request))

@api_view(['POST'])
@permission_classes([AllowAny])
def userlogin(request):
     pass



@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
     pass



    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def userdash(request):
    pass
