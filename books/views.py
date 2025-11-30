from django.shortcuts import render, redirect, get_object_or_404
from .models import Books

def library(request):
    books = Books.objects.all().order_by('-name')
    return render(request, 'library/library_website.html', {'books': books})

def book(request, book_id):
    book = get_object_or_404(Books, id = book_id)
    return render(request, 'library/book_detail_page.html', {'book': book})