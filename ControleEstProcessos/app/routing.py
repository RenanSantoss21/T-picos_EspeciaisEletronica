from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/telemetria/', consumers.TelemetriaConsumer.as_asgi()),
]
