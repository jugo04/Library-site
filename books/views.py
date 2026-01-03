from rest_framework import generics, viewsets
from .models import Books, Authors, Genre
from django_filters.rest_framework import DjangoFilterBackend
from .serializer import *

#Відображення списку книг на головній сторінці, деталі конкретної книги та список книг залежно від жанру
class LibraryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Books.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return LibrarySerializer

#Відображення списку авторів в розділі "Автори" та деталі конкретного автора.
class AuthorsModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Authors.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AuthorDetailSerializer
        return AuthorsSerializer

#Список жанрів відображений в розділі "Жанри"
class GenresAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
