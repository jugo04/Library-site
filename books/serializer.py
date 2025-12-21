from rest_framework import serializers
from .models import Books, Authors, Genre

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

#Необхідно додати:
#Відобаження деталей книги.
#Деталі автора зі списком книг які він випустив.
#Реалізувати пошук, та список книг при виборі жанру.
#ОнлайнРідер
#Авторизація та після цього реалізувати можливість обирати улюблені книги.
#відображення улюблених книг.