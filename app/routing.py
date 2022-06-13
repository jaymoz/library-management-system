from django.urls import path
from . import consumers


websocket_urlpatterns = [
    path('contact-admin/', consumers.ChatConsumer.as_asgi()),
]