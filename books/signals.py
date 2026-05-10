from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookStatus, Review, UserAchievement, Achievement

def grant_achievement(user, code):
    try:
        achievement = Achievement.objects.get(code = code)
        UserAchievement.objects.get_or_create(user = user, achievement = achievement)
    except Achievement.DoesNotExist:
        pass

@receiver(post_save, sender = BookStatus)
def chek_book_achievements(sender, instance, **kwargs):
    if not instance.is_read:
        return

    read_count = BookStatus.objects.filter(user = instance.user, is_read = True).count()
    if read_count == 1:
        grant_achievement(instance.user, 'first_book')

    book = instance.book
    if book.series:
        all_books = book.series.books_by_series.count()
        read_books = BookStatus.objects.filter(
            user = instance.user,
            book__series = book.series,
            is_read = True).count()
        if all_books == read_books:
            grant_achievement(instance.user, 'first_series')

@receiver(post_save, sender=Review)
def check_review_achievement(sender, instance, created, **kwargs):
    if created:
        grant_achievement(instance.user, 'first_review')