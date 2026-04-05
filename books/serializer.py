from django.db.models import BooleanField
from rest_framework import serializers
from .models import *
from django.db.models import Min, Max


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]

class SeriesShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ["id", "name"]

#Задаємо поля для файлу JSON з відображенням параметрів книги
class BookSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ('id', 'cover', 'name', 'genres')

    def get_genres(self, obj):
        return ', '.join([genre.name for genre in obj.genre.all()])


class SeriesDataMixin:
    def get_authors(self, obj):
        authors = Author.objects.filter(books_by_author__series=obj).distinct()
        return [author.name for author in authors]

    def get_genres(self, obj):
        genres = Genre.objects.filter(books_by_genre__series=obj).distinct()
        return [genre.name for genre in genres]

    def get_years(self, obj):
        years = obj.books_by_series.aggregate(
            start=Min('year'),
            end=Max('year')
        )
        return f"{years['start']} - {years['end']}"


class SeriesSerializer(SeriesDataMixin, serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = ["name", "books_count", "authors", "genres"]

    def get_books_count(self, obj):
        return obj.books_by_series.count()


class SeriesDetailSerializer(SeriesDataMixin, serializers.ModelSerializer):
    books = BookSerializer(source="books_by_series", many=True, read_only=True)
    authors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
    years = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = ["name", "description", "books", "authors", "genres", "years"]

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
    author = AuthorSerializer(many=True)
    genre = serializers.StringRelatedField(many=True)
    series = SeriesShortSerializer()
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