from django.db import models
from django.conf import settings


#Модель для жанрів з параметром "назва жанру"
class Genre(models.Model):
    genre = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ('genre',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'

    def __str__(self):
        return self.genre


#Модель для авторів з параметрами: ім`я, фото, біографія
class Author(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    photo = models.ImageField(upload_to='author_photo/', blank=True, null=True)
    birth_year = models.PositiveIntegerField()
    birth_place = models.TextField(max_length=100)
    biography = models.TextField()

    class Meta:
        ordering = ('name',)
        verbose_name = "Автор"
        verbose_name_plural = "Автори"

    def __str__(self):
        return self.name


#Модель з параметрами книги: назва, обкладинка, ім`я автора з попередньої моделі, жанр з попередньої моделі,
#рік випуску, опис та пдф файл з самою книгою
class Book(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    author = models.ForeignKey(Author, related_name='books_by_author', on_delete=models.CASCADE)
    genre = models.ManyToManyField(Genre, related_name='books_by_genre')
    year = models.PositiveIntegerField()
    description = models.TextField()
    file = models.FileField(upload_to='books_pdf/')

    class Meta:
        ordering = ('name',)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.name


class BookStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete= models.CASCADE)

    is_favorite = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = "Статус книги"
        verbose_name_plural = "Статус книги"