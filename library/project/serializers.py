from rest_framework import serializers

from .models import Book, Collection

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model= Book
        fieds = "__all__"

class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = "__all__"