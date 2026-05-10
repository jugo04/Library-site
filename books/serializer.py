from django.db.models import BooleanField
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

from .models import *
from django.db.models import Min, Max
from django.db.models import Avg, Count


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]

class SeriesShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Series
        fields = ["id", "name"]


class BookRaitingMixin:
    def get_average_rating(self, obj):
        from django.db.models import Avg
        result = obj.bookstatus_set.aggregate(avg=Avg('rating'))
        return round(result['avg'], 1) if result['avg'] else None


#Задаємо поля для файлу JSON з відображенням параметрів книги
class BookSerializer(BookRaitingMixin, serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = ('id', 'cover', 'name', 'genres', "average_rating", "price")

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

    def get_cover(self, obj):
        first_book = obj.books_by_series.filter(cover__isnull=False).first()
        if first_book:
            request = self.context.get('request')
            return request.build_absolute_uri(first_book.cover.url)
        return None


class SeriesSerializer(SeriesDataMixin, serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()
    authors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Series
        fields = ["id", "cover","name", "books_count", "authors", "genres"]

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
class BookDetailSerializer(BookRaitingMixin, serializers.ModelSerializer):
    author = AuthorSerializer(many=True)
    genre = serializers.StringRelatedField(many=True)
    series = SeriesShortSerializer()
    average_rating = serializers.SerializerMethodField()
    class Meta:
        model = Book
        fields = '__all__'


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
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)


class SubscriptionPlanListSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ("id", "name", "description", "price",)


class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Review
        fields = ('id', 'user', 'comment', 'created_at')


class PublicProfileSerializer(serializers.ModelSerializer):
    achievement = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ('id', 'username', 'photo', 'biography', 'achievement')

    def get_achievement(self, obj):
        requests = self.context.get('request')
        achievements = UserAchievement.objects.filter(user=obj)
        return [
            {
                'name': a.achievement.name,
                'icon': requests.build_absolute_uri(a.achievement.icon.url) if a.achievement.icon else None,
            }
                for a in achievements
                ]


class ProfileSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'photo', 'biography')
        read_only_fields = ('email',)


#Перегляд списку досягнень.
class AchievementListSerializer(serializers.ModelSerializer):
    is_earned = serializers.SerializerMethodField()

    class Meta:
        model = Achievement
        fields = ('id', 'name', 'description', 'icon', 'is_earned')

    def get_is_earned(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return UserAchievement.objects.filter(user=user, achievement=obj).exists()
        return False