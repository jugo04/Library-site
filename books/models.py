from django.db import models


class Genre(models.Model):
    genre = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ('genre',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'

    def __str__(self):
        return self.genre


class Authors(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    photo = models.ImageField(upload_to='author_photo/', blank=True, null=True)
    biography = models.TextField()

    class Meta:
        ordering = ('name',)
        verbose_name = "Автор"
        verbose_name_plural = "Автори"

    def __str__(self):
        return self.name

class Books(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    author = models.ForeignKey(Authors, related_name='books_by_author', on_delete=models.CASCADE)
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