from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import *
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializer import *
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q


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


#Реалізація пошуку, шукати можна авторів та книги залежно від типу пошуку (type = ??)
class SearchingAPIView(APIView):
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination
    def get(self, request):
        query = request.GET.get('q', '').strip()
        query_type = request.GET.get('type', '')

        if not query:
            return Response([])

        queryset = self.get_query(query_type)

        if queryset is None:
            return Response({'Error': 'Invalid search type'}, status=400)

        serializer_class = self.get_serializer(query_type)
        result = self.searching(query, queryset)

        serializer = serializer_class(result, many=True, context={'request': request})
        return Response(serializer.data)

    def get_query(self, query_type):
        if query_type == "author":
            queryset = Authors.objects.all()
            return queryset
        elif query_type == "books":
            queryset = Books.objects.all()
            return queryset
        return None

    def get_serializer(self, query_type):
        if query_type == "author":
            serializer = AuthorsSerializer
            return serializer
        elif query_type == "books":
            serializer = LibrarySerializer
            return serializer
        return None

    def searching(self, query, queryset):
        if len(query) < 3:
            return queryset.filter(name__icontains=query)

        words = query.split()

        q_objects = Q()
        for word in words:
            q_objects |= Q(name__icontains=word)
            q_objects |= Q(name__trigram_similar=word)

        queryset = queryset.filter(q_objects).distinct()

        queryset = queryset.annotate(
            similarity=TrigramSimilarity("name", query)
        ).order_by("-similarity")

        return queryset