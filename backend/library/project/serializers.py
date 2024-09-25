from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import Book, Collection

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model= Book
        fieds = ["title", "author", "description", "year", "isbn"]

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"

class userSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["Username", "email"]

    def create(self, validated_data):
        newuser = User(
            username = validated_data["username"],
            email = validated_data["email"]
        )
        newuser.set_password(validated_data["password"])

        newuser.save()

        return Response({
            "username": newuser.username,
            "email": newuser.email
        })