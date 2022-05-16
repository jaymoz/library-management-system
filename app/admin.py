from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Book)
admin.site.register(OrderItem)
admin.site.register(UserProfile)
admin.site.register(IssuedBooks)
admin.site.register(Category)