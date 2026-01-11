from rest_framework.decorators import action
from rest_framework.response import Response
from .models import *
from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import *


#Відображення списку книг на головній сторінці, деталі конкретної книги та список книг залежно від жанру
#Декоратор action для того, щоб обирати улюблену книгу авторизованому користувачу
class LibraryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Books.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre']
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return LibrarySerializer

    @action(detail = True, methods = ['post'], permission_classes = [IsAuthenticated])
    def like(self, request, pk=None):
        book = self.get_object()
        user_book, created = BookStatus.objects.get_or_create(user=request.user, book=book)

        user_book.is_favorite = not user_book.is_favorite
        user_book.save()

        return Response({'book': book.name, 'liked': user_book.is_favorite})

#Відображення списку авторів в розділі "Автори" та деталі конкретного автора.
class AuthorsModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Authors.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AuthorDetailSerializer
        return AuthorsSerializer

#Список жанрів відображений в розділі "Жанри"
class GenresAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [AllowAny]


class FavoriteBooksModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return BookStatus.objects.filter(
            user = self.request.user,
            is_favorite = True
        )
    serializer_class = FavoriteBookSerializer
    permission_classes = [IsAuthenticated]
