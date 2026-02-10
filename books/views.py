from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import *
from rest_framework import generics, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import *


#Клас для пагінації сторінок
class LibraryApiListPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page_size'
    max_page_size = 200

#Відображення списку книг на головній сторінці, деталі конкретної книги та список книг залежно від жанру
#Декоратор action для того, щоб обирати улюблену книгу авторизованому користувачу
class LibraryModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Books.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre']
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return LibrarySerializer

    @action(detail = True, methods = ['post'], permission_classes = [IsAuthenticated])
    def interact(self, request, pk=None):
        serializer = BookInteractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        book = self.get_object()
        user_book, created = BookStatus.objects.get_or_create(user=request.user, book=book)

        if 'like' in data:
            user_book.is_favorite = data['like']
        if 'read' in data:
            user_book.is_read = data['read']

        user_book.save()

        return Response({
            'book': book.name,
            'like': user_book.is_favorite,
            'read': user_book.is_read
        })


#Відображення списку авторів в розділі "Автори" та деталі конкретного автора.
class AuthorsModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Authors.objects.all()
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AuthorDetailSerializer
        return AuthorsSerializer

#Список жанрів відображений в розділі "Жанри"
class GenresAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenresSerializer
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination

#Список улюблених книг користувача
class FavoriteBooksModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return BookStatus.objects.filter(
            user = self.request.user,
            is_favorite = True
        )
    serializer_class = FavoriteAndReadedBookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LibraryApiListPagination


#Список прочитаних книг користувача
class ReadedBooksModelViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return BookStatus.objects.filter(
            user = self.request.user,
            is_read = True
        )
    serializer_class = FavoriteAndReadedBookSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LibraryApiListPagination
