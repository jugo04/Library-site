from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce


#Базова модель User, має лише базові параметри, можна буде в подальшому налаштовувати.
#Треба додати необхідні поля для профілю
class User(AbstractUser):
    photo = models.ImageField(upload_to='user_avatar/', blank=True, null=True)
    birth_date = models.DateField( blank=True, null=True)
    biography = models.CharField(max_length=300, blank=True, null=True)


#Модель для жанрів з параметром "назва жанру"
class Genre(models.Model):
    name = models.CharField(max_length=100, db_index=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанри'

    def __str__(self):
        return self.name


#Модель для авторів з параметрами: ім`я, фото, біографія
class Author(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    photo = models.ImageField(upload_to='author_photo/', blank=True, null=True)
    birth_year = models.PositiveIntegerField(blank=True, null=True)
    birth_place = models.TextField(max_length=100, blank=True, null=True)
    biography = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('name',)
        verbose_name = "Автор"
        verbose_name_plural = "Автори"

    def __str__(self):
        return self.name


#Серія книг, містить назву серії та її опис
class Series(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()

    class Meta:
        ordering = ('name',)
        verbose_name = 'Серія'
        verbose_name_plural = 'Серії'

    def __str__(self):
        return self.name


#Вікова категорія для моделі Book
class AgeCategory(models.IntegerChoices):
    ALL = 0, '0+'
    TEEN = 12, '12+'
    MATURE = 16, '16+'
    ADULT = 18, '18+'


#Модель з параметрами книги: назва, серія книг, обкладинка, ім`я автора з попередньої моделі, жанр з попередньої моделі,
#рік випуску, опис та пдф файл з самою книгою
class Book(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    series = models.ForeignKey(
        Series, related_name='books_by_series', null=True, blank=True, on_delete=models.SET_NULL)

    cover = models.ImageField(upload_to='cover/', blank=True, null=True)
    author = models.ManyToManyField(
        Author, related_name='books_by_author')

    genre = models.ManyToManyField(
        Genre, related_name='books_by_genre')

    year = models.PositiveIntegerField()
    description = models.TextField()
    file = models.FileField(upload_to='books_pdf/')
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    age_category = models.PositiveSmallIntegerField(
        choices=AgeCategory.choices,
        default=AgeCategory.ALL
    )

    @classmethod
    def get_with_rating(cls):
        return cls.objects.annotate(
            avg=Avg('bookstatus__rating'),
            count=Count('bookstatus__rating'),
            weighted=(
                (Coalesce(Count(
                    'bookstatus__rating'), 0) * Coalesce(Avg('bookstatus__rating'), 0.0)) + (10 * 3.0)
            ) / (Coalesce(Count('bookstatus__rating'), 0) + 10)
        ).order_by('-weighted')

    class Meta:
        ordering = ('name',)
        verbose_name = "Книга"
        verbose_name_plural = "Книги"

    def __str__(self):
        return self.name


#Відповідає за статус книги "Прочиано", "вподобано" для авторизованого користувача
class BookStatus(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete= models.CASCADE)

    is_favorite = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self):
        return f'{self.user} - {self.book}'

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = "Статус книги"
        verbose_name_plural = "Статус книги"


#Модель відгуків на книги, має поля користувача, книги та самого відгуку і коли створено
class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.book}"

    class Meta:
        unique_together = ('user', 'book')
        ordering = ('-created_at',)
        verbose_name = "Відгук"
        verbose_name_plural = "Відгуки"


#Досягнення користувачів
class Achievement(models.Model):
    code = models.CharField(max_length=100, db_index=True)
    icon = models.ImageField(upload_to='achiev_icon/')
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Досягнення"
        verbose_name_plural = "Досягнення"


#Досягнення конкретного користувача
class UserAchievement(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    achievement = models.ForeignKey(
        Achievement,  related_name = 'user_achievements', on_delete=models.CASCADE)
    issue_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.achievement}'


#Вартість книг без наявної підписки
class BookPurchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    payment_id = models.CharField(max_length=255, blank=True)
    price_paid = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.user} - {self.book}"

    class Meta:
        unique_together = ('user', 'book')
        verbose_name = "Покупка книги"
        verbose_name_plural = "Покупки книг"


#Рівні підписки
class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_family = models.BooleanField(default=False)
    max_family_members = models.PositiveIntegerField(null=True, blank=True)
    duration_days = models.PositiveIntegerField()
    has_pdf_access = models.BooleanField(default=False)
    book_limit = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тарифний план'
        verbose_name_plural = 'Тарифні плани'


#Підписка конкретного користувача
class UserSubscription(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    payment_id = models.CharField(max_length=255, blank=True)
    subscription = models.ForeignKey(
        SubscriptionPlan, related_name='user_subscription', on_delete=models.PROTECT
    )
    start_date = models.DateTimeField(auto_now_add=True)
    date_expire = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user} - {self.subscription}'


#Група сім'ї для сімейної підписки
class FamilyGroup(models.Model):
    name = models.CharField(max_length=100, blank=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='owned_family_group', on_delete = models.CASCADE)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='member_family_group', blank=True)
    max_members = models.PositiveIntegerField(default=4)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Сімейна група'
        verbose_name_plural = 'Сімейні групи'

#запрошення до сімейної підписки
class FamilyInvite(models.Model):
    group = models.ForeignKey(
        FamilyGroup,
        on_delete=models.CASCADE,
        related_name='invites'
    )
    invited_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='family_invites'
    )
    accepted = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.group} - {self.invited_user}'

    class Meta:
        unique_together = ('group', 'invited_user')
        verbose_name = "Запрошення до сімейної групи"
        verbose_name_plural = "Запрошення до сімейних груп"