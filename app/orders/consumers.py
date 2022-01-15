from channels.generic.websocket import AsyncJsonWebsocketConsumer
from orders.serializers import OrderProductSerializer, ReadOnlyOrderSerializer, OrderSerializer, UpdateOrderSerializer
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
            print('## Anonymous user connected')
        else:
            channel_groups = []
            # Get user groups
            user_group = await self._get_user_group(self.scope['user'])

            # If user is vendor add him according premises channel
            print("## User connected as", user_group)
            if str(user_group) == 'vendor':
                channel_groups.append(self.channel_layer.group_add(
                    group='vendor',
                    channel=self.channel_name
                ))
                premises_id = await self._get_vendor_premises(user)
                print('## Vendor is added to premises channel', str(premises_id))
                channel_groups.append(self.channel_layer.group_add(
                    group=str(premises_id),
                    channel=self.channel_name
                ))


            orderset = await self._get_orders(self.scope['user'])
            self.orders = set(orderset)

            for order in self.orders:
                print("Customer added to channel - ", order)
                channel_groups.append(
                    self.channel_layer.group_add(order, self.channel_name))
            asyncio.gather(*channel_groups)
            await self.accept()

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        print(message_type)

        if message_type == 'create.order':
            await self.create_order(content)
        if message_type == 'update.order':
            await self.update_order(content)
        if message_type == 'accept.order':
            await self.accept_order(content)
        if message_type == 'ready.order':
            await self.ready_order(content)
        if message_type == 'test':
            await self.send_json({
                'type': 'testresponse',
                'data': content
            })

    # async def echo_message(self, event):
    #     print("ECHO MESSAGE", event.get('data').get('id'))
    #     await self.send_json(event)

    async def order_notification(self, event):
        print("ECHO MESSAGE", event.get('data').get('id'))
        await self.send_json(event)

    async def accept_order(self, event):
        my_dict = defaultdict(dict)
        event['data'].update({"status" : "ACCEPTED"})
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
        order_data = await self._deserialize_order(order)

        # send user requests to premises group.
        premises_channel = order_data.get('premises').get('id')

        await self.channel_layer.group_send(group=str(premises_channel), message={
            'type': 'order.notification',
            'data': order_data
        })

        # Handle only if order is not being tracked.
        print("## Order is sent to channel", str(premises_channel))
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

        order_data = await self._deserialize_order(order)

        # send updates to customers that subscribe to this order.
        print("Order updates sending response to group", order_id)


        # await self.channel_layer.group_send(group=order_id, message={
        #     'type': 'echo.message',
        #     'data': order_data
        # })

        await self.channel_layer.group_send(group=order_id, message={
            'type': 'order.notification',
            'data': order_data
        })

        # handle add only if order is not being tracked.
        # this happens when a vendors accept a request.
        if order_id not in self.orders:
            self.orders.add(order_id)
            await self.channel_layer.group_add(
                group=order_id,
                channel=self.channel_name
            )

        # This goes to vendor
        await self.send_json({
            'type': 'update_order',
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
    def _create_order(self, content):
        # Pop products from order and validate seperatly
        order_products = content.pop('order_products')
        print("## Order content passed to serailizer 1", content)
        order_serializer = OrderSerializer(data=content)
        # Do not validate Order Products since it does not exists on model
        # TODO validate order products
        order_serializer.is_valid(raise_exception=True)
        data = {'order_products': order_products, **order_serializer.validated_data}
        print("## Order data used in create method 2", data)
        order = order_serializer.create(data)
        # order = order_serializer.create(order_serializer.validated_data)
        print('## Created order with id 3', order)
        return order

    @database_sync_to_async
    def _deserialize_order(self, order):
        data = ReadOnlyOrderSerializer(order).data
        return data

    @database_sync_to_async
    def _get_orders(self, user):
        if not user.is_authenticated:
            raise Exception('User is not authenticated.')
        user_groups = user.groups.values_list('name', flat=True)
        if 'vendor' in user_groups:
            # TODO - TAKE PREMISES FROM PARAMETER NOT FIRST
            orders = user.user_premises.first().orders_as_premises.exclude(
                status=Order.COMPLETED
            ).only('id').values_list('id', flat=True)
        else:
            orders = user.orders_as_customer.exclude(
                status=Order.COMPLETED
            ).only('id').values_list('id', flat=True)
        return [str(orderid) for orderid in orders]

    @database_sync_to_async
    def _update_order(self, content):
        instance = Order.objects.get(id=content.get('order'))
        serializer = UpdateOrderSerializer(data=content, partial=True)
        serializer.is_valid(raise_exception=True)
        order = serializer.update(instance, serializer.validated_data)
        return order

    @database_sync_to_async
    def _get_user_group(self, user):
        if not user.is_authenticated:
            raise Exception('User is not authenticated.')
        return user.groups.first()

    @database_sync_to_async
    def _get_vendor_premises(self, vendor):
        return vendor.user_premises.first().id
