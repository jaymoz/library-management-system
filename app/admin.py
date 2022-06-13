from django.contrib import admin
from .models import *
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q

#Register your models here.
admin.site.register(Book)
admin.site.register(OrderItem)
admin.site.register(UserProfile)
admin.site.register(IssuedBooks)
admin.site.register(Category)
admin.site.register(ChatMessage)

class ChatMessage(admin.TabularInline):
    model = ChatMessage

class ThreadAdmin(admin.ModelAdmin):
    inlines = [ChatMessage]
    class Meta:
        model = Thread

admin.site.register(Thread, ThreadAdmin)