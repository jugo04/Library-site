from django.db.models import BooleanField
from rest_framework import serializers
from .models import *

#Задаємо поля для файлу JSON з відображенням параметрів книги
class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('id', 'cover', 'name', 'genre')

#Задаємо поля для файлу JSON з відображенням параметрів автора
class AuthorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Authors
        fields = ('id', 'photo', 'name')

#Задаємо поля для файлу JSON з відображенням жанру
class GenresSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('genre',)

#Деталі книги
class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Books
        fields = ('__all__')

#Деталі автора:
class AuthorDetailSerializer(serializers.ModelSerializer):
    books_by_author = LibrarySerializer(many=True, read_only=True)
    class Meta:
        model = Authors
        fields = ('id', 'name', 'photo', 'biography', 'books_by_author')


class FavoriteAndReadedBookSerializer(serializers.ModelSerializer):
    book = LibrarySerializer(read_only=True)
    class Meta:
        model = BookStatus
        fields = ('book',)

class BookInteractSerializer(serializers.Serializer):
    like = serializers.BooleanField(required=False)
    read = serializers.BooleanField(required=False)