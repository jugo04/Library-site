from django.urls import path
from . import views

urlpatterns = [
    path('', views.library, name = 'library'),
    path('<int:book_id>/', views.book, name= 'book'),
    path('authors/', views.authors, name = 'authors'),
    path('genres/', views.genres, name = 'genres'),
]