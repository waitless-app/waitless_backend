from channels.generic.websocket import AsyncJsonWebsocketConsumer
from orders.serializers import ReadOnlyOrderSerializer, OrderSerializer, UpdateOrderSerializer
from channels.db import database_sync_to_async
from core.models import Order
from collections import defaultdict
from django.utils import timezone
import asyncio


class NotificationConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, scope):
        super().__init__(scope)

        # Keep track of the user's orders.
        self.orders = set()

    async def connect(self):
        user = self.scope['user']
        if user.is_anonymous:
            await self.close()
        else:
            channel_groups = []

            # Get user groups
            user_group = await self._get_user_group(self.scope['user'])

            # If user is vendor add him to vendor group
            if user_group == 'vendor':
                channel_groups.append(self.channel_layer.group_add(
                    group='vendor',
                    channel=self.channel_name
                ))

            # tu jest cos pojebane ale dziala
            orderset = await self._get_orders(self.scope['user'])
            self.orders = set(orderset)

            for order in self.orders:
                channel_groups.append(
                    self.channel_layer.group_add(order, self.channel_name))
            asyncio.gather(*channel_groups)
            await self.accept()
            await self.send_json({'group' : user_group})

    async def receive_json(self, content, **kwargs):
        # ADD try to check json
        message_type = content.get('type')
        if message_type == 'create.order':
            await self.create_order(content)
        if message_type == 'test':
            await self.send_json({
                'type': 'testresponse',
                'data': content
            })
        if message_type == 'update.order':
            await self.update_order(content)
        if message_type == 'accept.order':
            await self.accept_order(content)
        if message_type == 'ready.order':
            await self.ready_order(content)

    async def echo_message(self, event):
        await self.send_json(event)

    async def accept_order(self, event):
        my_dict = defaultdict(dict)
        event['data'].update({"status" : "ACCEPTED"})
        await self.send_json({'data' : event})
        await self.update_order(event)
    
    async def ready_order(self, event):
        my_dict = defaultdict(dict)
        event['data'].update({"status" : "READY", "ready_time" : timezone.now()})
        await self.update_order(event)

    async def collect_order(self, event):
        my_dict = defaultdict(dict)
        event['data'].update({"status" : "COMPLETED", "collected_time" : timezone.now()})
        await self.update_order(event)

    async def create_order(self, event):
        order = await self._create_order(event.get('data'))
        order_id = f'{order.id}'
        order_data = ReadOnlyOrderSerializer(order).data

        # send user requests to all vendors.
        await self.channel_layer.group_send(group='vendor', message={
            'type': 'echo.message',
            'data': order_data
        })
        # Handle only if order is not being tracked.
        if order_id not in self.orders:
            self.orders.add(order_id)
            # add this channel to new order group.
            await self.channel_layer.group_add(
                group=order_id,
                channel=self.channel_name
            )

        await self.send_json({
            'type': 'create.order',
            'data': order_data
        })

    async def update_order(self, event):
        order = await self._update_order(event.get('data'))
        order_id = f'{order.id}'
        # await self.send_json({'data': str(order)})
        order_data = ReadOnlyOrderSerializer(order).data

        # send updates to vendors that subscribe to this order.
        await self.channel_layer.group_send(group=order_id, message={
            'type': 'echo.message',
            'data': order_data
        })

        # handle add only if trip is not being tracked.
        # this happens when a vendors accept a request.
        if order_id not in self.orders:
            self.orders.add(order_id)
            await self.channel_layer.group_add(
                group=order_id,
                channel=self.channel_name
            )

        await self.send_json({
            'type': 'update_trip',
            'data': order_data
        })
    async def disconnect(self, code):
        # Remove this channel from every order group.
        channel_groups = [
            self.channel_layer.group_discard(
                group=order,
                channel=self.channel_name
            )
            for order in self.orders
        ]
        user_group = await self._get_user_group(self.scope['user'])
        if user_group == 'vendor':
            channel_groups.append(self.channel_layer.group_discard(
                group='vendor',
                channel=self.channel_name
            ))
        asyncio.gather(*channel_groups)
        self.orders.clear()

        await super().disconnect(code)

    @database_sync_to_async
    def get_order_data(order):
        return ReadOnlyOrderSerializer(order).data

    @database_sync_to_async
    def _create_order(self, content):
        serializer = OrderSerializer(data=content)
        serializer.is_valid(raise_exception=True)
        order = serializer.create(serializer.validated_data)
        return order

    @database_sync_to_async
    def _get_orders(self, user):
        if not user.is_authenticated:
            raise Exception('User is not authenticated.')
        user_groups = user.groups.values_list('name', flat=True)
        if 'vendor' in user_groups:
            orders = user.orders_as_vendor.exclude(
                status=Order.COMPLETED
            ).only('id').values_list('id', flat=True)
        else:
            orders = user.orders_as_customer.exclude(
                status=Order.COMPLETED
            ).only('id').values_list('id', flat=True)
        return [str(orderid) for orderid in orders]

    @database_sync_to_async
    def _update_order(self, content):
        instance = Order.objects.get(id=content.get('id'))
        serializer = UpdateOrderSerializer(data=content, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.update(instance, serializer.validated_data)
        return order

    @database_sync_to_async
    def _get_user_group(self, user):
        if not user.is_authenticated:
            raise Exception('User is not authenticated.')
        return user.groups.first().name
