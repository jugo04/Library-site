"""
URL configuration for WebLibrary project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from books.views import LibraryAPIView, AuthorsAPIView, GenresAPIView, BookDetailAPIView, AuthorDetailAPIView

urlpatterns = [
    path('api/library', LibraryAPIView.as_view()),
    path('api/Authors', AuthorsAPIView.as_view()),
    path('api/Genres', GenresAPIView.as_view()),
    path('api/Book', GenresAPIView.as_view()),
    path("books/<int:pk>/", BookDetailAPIView.as_view(), name="book-detail"),
    path("author/<int:pk>/", AuthorDetailAPIView.as_view(), name="author-detail"),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
