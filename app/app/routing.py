from channels.routing import ProtocolTypeRouter, URLRouter
from orders.consumers import OrderConsumer
from django.urls import path
from .middleware.channelsmiddleware import TokenAuthMiddlewareStack

channel_routing = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter([
            path('notification/', OrderConsumer),
        ])
    )
}
)
