from django.db.models import BooleanField
from rest_framework import serializers
from .models import *

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]

#Задаємо поля для файлу JSON з відображенням параметрів книги
class BookSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ('id', 'cover', 'name', 'genres')

    def get_genres(self, obj):
        return ', '.join([genre.genre for genre in obj.genre.all()])

#Задаємо поля для файлу JSON з відображенням параметрів автора
class AuthorsSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    class Meta:
        model = Author
        fields = ('id', 'photo', 'name', 'books_count')

    def get_books_count(self, obj):
        return obj.books_by_author.count()

#Задаємо поля для файлу JSON з відображенням жанру
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name',)

#Деталі книги
class BookDetailSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = serializers.StringRelatedField(many=True)
    class Meta:
        model = Book
        fields = ('__all__')

#Деталі автора:
class AuthorDetailSerializer(serializers.ModelSerializer):
    books_by_author = BookSerializer(many=True, read_only=True)
    class Meta:
        model = Author
        fields = ('id', 'name', 'photo', 'biography', 'books_by_author', 'birth_year', 'birth_place')


class FavoriteAndReadedBookSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    class Meta:
        model = BookStatus
        fields = ('book',)

class BookInteractSerializer(serializers.Serializer):
    like = serializers.BooleanField(required=False)
    read = serializers.BooleanField(required=False)