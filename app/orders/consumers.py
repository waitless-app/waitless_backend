from channels.consumer import AsyncConsumer


class NotificationConsumer(AsyncConsumer):

    async def websocket_connect(self, event):
        # accept all connetcions
        await self.send({
            "type": "websocket.accept"
        })

    async def websocket_receive(self, event):
        await self.send({
            "type": "websocket.send",
            "text": event["text"],
        })
