from channels.routing import ProtocolTypeRouter, URLRouter
from orders.consumers import NotificationConsumer
from django.urls import path

channel_routing = ProtocolTypeRouter({
    'websocket': URLRouter([
        path('notification/', NotificationConsumer),
    ])
})
