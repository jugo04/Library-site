from django.contrib import admin
from .models import Books, Authors, Genre

admin.site.register(Genre)
admin.site.register(Authors)
admin.site.register(Books)