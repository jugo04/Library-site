from rest_framework import generics
from .models import Books, Authors, Genre
from .serializer import LibrarySerializer, AuthorsSerializer, GenresSerializer

#Відображення списку книг на головній сторінці
class LibraryAPIView(generics.ListAPIView):
    queryset = Books.objects.all()
    serializer_class = LibrarySerializer

#Відображення списку авторів в розділі "Автори"
class AuthorsAPIView(generics.ListAPIView):
    queryset = Authors.objects.all()
    serializer_class = AuthorsSerializer

#Список жанрів відображений в розділі "Жанри"
class GenresAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer