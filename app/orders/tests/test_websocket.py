from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import Group
from core.models import Order
import pytest

from app.routing import channel_routing

TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


@database_sync_to_async
def create_user(email, password):
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
        name="Mike Tayson"
    )
    return user


@database_sync_to_async
def create_employee(email, password):
    user = get_user_model().objects.create_user(
        email=email,
        password=password,
        name="Mike Tayson"
    )

    user_group, _ = Group.objects.get_or_create(name="employee")
    user.groups.add(user_group)
    user.save()
    return user


@database_sync_to_async
def create_order(**kwargs):
    return Order.objects.create(**kwargs)


async def auth_connect(user):
    access = AccessToken.for_user(user)
    communicator = WebsocketCommunicator(
        application=channel_routing,
        path=f'/notification/?token={access}',
    )
    connected, _ = await communicator.connect()
    assert connected is True
    return communicator


async def connect_and_create_order(
    *,
    user,
    status
):
    communicator = await auth_connect(user)
    await communicator.send_json_to({
        'type': 'create.order',
        'data': {
            'status': status,
            'user': user.id
        }
    })
    return communicator


async def connect_and_update_order(*, user, order, status):
    communicator = await auth_connect(user)
    await communicator.send_json_to({
        'type': 'update.order',
        'data': {
            'id': f'{order.id}',
            'status': status

        }
    })
    return communicator


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
class TestWebSocket:
    async def test_unauthorized_user_cannot_connect_to_socket(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = WebsocketCommunicator(
            application=channel_routing,
            path='/notification/'
        )
        connected, _ = await communicator.connect()
        assert connected is False

    async def test_user_can_connect_to_server(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        user = await create_user(
            'test@user.pl', 'password'
        )
        communicator = await auth_connect(user)
        await communicator.disconnect()

    async def test_user_can_create_an_order(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        user = await create_user(
            email="user2@avocado.pl",
            password="enchilada"
        )
        communicator = await connect_and_create_order(
            user=user,
            status='REQUESTED'
        )

        response = await communicator.receive_json_from()
        data = response.get('data')

        assert 'REQUESTED' == data['status']

    async def test_user_is_added_to_order_groups_on_connect(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        user = await create_user(
            email='user1@avocado.io',
            password='PASWW0RD'
        )

        communicator = await connect_and_create_order(
            user=user,
            status='REQUESTED'
        )

        response = await communicator.receive_json_from()
        data = response.get('data')

        order_id = data['id']
        message = {
            'type': 'echo.message',
            'data': 'This is test message'
        }

        channel_layer = get_channel_layer()
        await channel_layer.group_send(order_id, message=message)

        response = await communicator.receive_json_from()

        assert message == response

        await communicator.disconnect()

    async def test_user_is_added_to_order_groups_on_init(self, settings):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        user = await create_user(
            email='user2@avocado.pl',
            password='PASSW01RDS'
        )

        order = await create_order(
            status="REQUESTED",
            user=user
        )

        # user should be added to users groups
        communicator = await auth_connect(user)

        message = {
            'type': 'echo.message',
            'data': 'This is test message'
        }

        channel_layer = get_channel_layer()
        await channel_layer.group_send(f'{order.id}', message=message)

        response = await communicator.receive_json_from()
        assert message == response

        await communicator.disconnect()
