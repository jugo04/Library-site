from django.db import models

class Books(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    author = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    description = models.TextField()
    file = models.FileField(upload_to='books_pdf/')

    class Meta:
        ordering = ('name',)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.name