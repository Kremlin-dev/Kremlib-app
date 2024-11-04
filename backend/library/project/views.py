from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from .models import Book, Collection
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import BookSerializer, CollectionSerializer, UserSerializer
from rest_framework.response import Response

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data = request.data)

    if serializer.is_valid():
        user = serializer.save

        refresh = RefreshToken.for_user(user)
        access = refresh.access_token

        return Response({
               "message": "Signup was successful",
               "refresh": str(refresh),
               "access": str(access),
               "username": user.username
          })
    return Response({"message": "User data could not be validated"})

@api_view(["POST"])
@permission_classes([AllowAny])
def login(request):
    serializer = TokenObtainPairSerializer(data = request.data)

    if serializer.is_valid():
         tokens = serializer.validated_data

         refresh = tokens['refresh']
         access =  tokens['access']

         return Response({
              "message": "Login was a success",
              "refresh": str(refresh),
              "access": str(access)
         })
    return Response({"message": "Data could not be validated"})








# @api_view(["GET"])
# def get_allbooks(request):
#     query = request.GET.get("query")
#     search_by = request.GET.get("search_by")

#     if not query and not search_by:
#                 books = Book.objects.all()[:10]

#     else:
#         if search_by == 'title':
#             books = Book.objects.filter(title__icontains=query)

#         elif search_by == 'author':
#             books = Book.objects.filter(author__icontains=query)

#         elif search_by == 'isbn':
#             books = Book.objects.filter(isbn__icontains=query)

#     context = {
#             'books':books,

#         }
#     template = loader.get_template('home.html')
#     return HttpResponse(template.render(context, request))


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
     serialiizer = userSerializer(data = request.data)

     if serialiizer.is_valid():
          serialiizer.save()

          return Response(serialiizer.data)
@api_view(['POST'])
@permission_classes([AllowAny])
def userlogin(request):
     serializer = TokenObtainPairSerializer(data = request.data)

     if serializer.is_valid():
          
          user = serializer.user

          refresh = RefreshToken.for_user(user)
          access = refresh.access_token
          
          return Response({
               "username": user.username,
               "email": user.email,
               "access": str(access),
               "refresh": str(refresh)
          })
    
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def userdash(request):
    pass
