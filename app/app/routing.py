from channels.routing import ProtocolTypeRouter, URLRouter
from orders.consumers import NotificationConsumer
from django.urls import path
from .middleware.channelsmiddleware import TokenAuthMiddleware

channel_routing = ProtocolTypeRouter({
    'websocket': TokenAuthMiddleware(
        URLRouter([
        path('notification/', NotificationConsumer),
    ])
    )
}
)
