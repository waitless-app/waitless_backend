from channels.generic.websocket import AsyncJsonWebsocketConsumer
from orders.serializers import ReadOnlyOrderSerializer, OrderSerializer
from channels.db import database_sync_to_async
from pprint import pprint

class NotificationConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        user = self.scope['user']        
        await self.accept()

    async def receive_json(self, content, **kwargs):
        message_type = content.get('type')
        if message_type ==  'create.order':
            await self.create_order(content)
        if message_type == 'test':
            await self.send_json({
            'type': 'testresponse',
            'data' : content
        })
    
    async def create_order(self, event):
        order = await self._create_order(event.get('data'))
        order_data = ReadOnlyOrderSerializer(order).data
        await self.send_json({
            'type': 'create.order',
            'data' : order_data
        })
    
    @database_sync_to_async
    def _create_order(self, content):
        serializer = OrderSerializer(data=content)
        serializer.is_valid(raise_exception= True)
        order = serializer.create(serializer.validated_data)
        return order