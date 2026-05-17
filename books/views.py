from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import *
from rest_framework import generics, viewsets
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny, IsAuthenticated, BasePermission
from .serializer import *
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q, Avg, Count
from datetime import date

#Клас для пагінації сторінок
class LibraryApiListPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page_size'
    max_page_size = 200


#Перевірка віку:
class AgePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        print(f'Перевірка віку: {obj.age_category}, юзер: {request.user}')
        if obj.age_category == 0:
            return True

        if not request.user.is_authenticated:
            return False

        if not request.user.birth_date:
            return False

        today = date.today()
        age = today.year - request.user.birth_date.year

        return age >= obj.age_category


#Відображення списку книг на головній сторінці, деталі конкретної книги та список книг залежно від жанру
#Декоратор action для того, щоб обирати улюблену книгу авторизованому користувачу
#Інший декоратор для створення та перегляду відгуків
class BookModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.get_with_rating()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['genre']
    pagination_class = LibraryApiListPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action == 'interact':
            return [IsAuthenticated(), AgePermission()]
        if self.action in ['retrieve', 'reviews']:
            return [AgePermission()]
        return [AllowAny()]

    @action(detail = True, methods = ['post'], permission_classes = [IsAuthenticated])
    def interact(self, request, pk=None):
        serializer = BookInteractSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user_book, created = BookStatus.objects.get_or_create(user=request.user, book=self.get_object())

        if 'like' in data:
            user_book.is_favorite = data['like']
        if 'read' in data:
            user_book.is_read = data['read']
        if 'rating' in data:
            user_book.rating = data['rating']

        user_book.save()

        return Response({
            'book': user_book.book.name,
            'like': user_book.is_favorite,
            'read': user_book.is_read,
            'rating': user_book.rating
        })

    @action(detail=True, methods=['get', 'post'], url_path='reviews')
    def reviews(self, request, pk=None):
        book = self.get_object()

        if request.method == 'GET':
            reviews = Review.objects.filter(book=book)
            serializer = ReviewSerializer(reviews, many=True)
            return Response(serializer.data)

        if request.method == 'POST':
            if not request.user.is_authenticated:
                return Response({'error': 'Потрібна авторизація'}, status=401)
            if Review.objects.filter(user=request.user, book=book).exists():
                return Response({'error': 'Ви вже залишали відгук на цю книгу'}, status=400)
            serializer = ReviewSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, book=book)
            return Response(serializer.data, status=201)

        return Response({'error': 'Метод не дозволений'}, status=405)


class SeriesModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Series.objects.all()
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return SeriesDetailSerializer
        return SeriesSerializer
    

#Відображення списку авторів в розділі "Автори" та деталі конкретного автора.
class AuthorModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Author.objects.all()
    permission_classes = [AllowAny]
    pagination_class = LibraryApiListPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AuthorDetailSerializer
        return AuthorsSerializer


#Список жанрів відображений в розділі "Жанри"
class GenreAPIView(generics.ListAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
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


#Відображення списку підписок
class SubscriptionPlanModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanListSerializer
    permission_classes = [AllowAny]


#Реалізація пошуку, шукати можна авторів та книги залежно від типу пошуку (type = ??)
class SearchingAPIView(APIView):
    permission_classes = [AllowAny]
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

        paginator = LibraryApiListPagination()
        page = paginator.paginate_queryset(result, request)

        serializer = serializer_class(page, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def get_query(self, query_type):
        if query_type == "author":
            queryset = Author.objects.all()
            return queryset
        elif query_type == "books":
            queryset = Book.get_with_rating()
            return queryset
        elif query_type == "series":
            queryset = Series.objects.all()
            return queryset
        return None

    def get_serializer(self, query_type):
        if query_type == "author":
            serializer = AuthorsSerializer
            return serializer
        elif query_type == "books":
            serializer = BookSerializer
            return serializer
        elif query_type == "series":
            serializer = SeriesSerializer
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


#Профіль користувача який може переглянути будь хто
class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = PublicProfileSerializer
    permission_classes = [AllowAny]


#Налаштування профілю в якого є доступ лише у користувача якому цей профіль належить
class ProfileSettingView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSettingSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

class AchievementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Achievement.objects.all()
    serializer_class = AchievementListSerializer
    permission_classes = [IsAuthenticated]