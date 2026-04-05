from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookStatus)
admin.site.register(Series)