from django import template
from app.models import *

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = IssuedBooks.objects.filter(user=user, ordered=False)
        if qs.exists():
            return qs[0].books.count()
    return 0