from django.contrib import admin
from .models import *

admin.site.register(Genre)
admin.site.register(Authors)
admin.site.register(Books)
admin.site.register(BookStatus)