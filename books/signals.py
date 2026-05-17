from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import *


#Виидалення файлів які більше не використовуються:

@receiver(post_delete, sender=Book)
def delete_book_files(sender, instance, **kwargs):
    if instance.cover:
        instance.cover.delete(save=False)
    if instance.file:
        instance.file.delete(save=False)

@receiver(post_delete, sender=Author)
def delete_author_files(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)

@receiver(post_delete, sender=User)
def delete_user_files(sender, instance, **kwargs):
    if instance.photo:
        instance.photo.delete(save=False)

@receiver(post_delete, sender=Achievement)
def delete_achievement_files(sender, instance, **kwargs):
    if instance.icon:
        instance.icon.delete(save=False)


#Досягнення користувача:

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


