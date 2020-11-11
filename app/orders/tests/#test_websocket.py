from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import Group
from core.models import Order, Premises, Menu, Product

import pytest

from app.routing import channel_routing

TEST_CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}


async def auth_connect(user):
    access = AccessToken.for_user(user)
    communicator = WebsocketCommunicator(
        application=channel_routing,
        path=f'/notification/?token={access}',
    )
    connected, _ = await communicator.connect()
    assert connected is True
    return communicator


@database_sync_to_async
def create_order(**kwargs):
    return Order.objects.create(**kwargs)

@pytest.fixture()
def customer():
    user = get_user_model().objects.create_user(
        email='user@user.com',
        password='password',
        name="Mike Tayson"
    )
    return user


@database_sync_to_async
@pytest.fixture()
def premises():
    owner = get_user_model().objects.create_user(email='owner@onboard.io', password='password')
    premises = Premises.objects.create(
        name='Pizzarini',
        city='Warsaw',
        owner=owner
    )
    return premises


@database_sync_to_async
@pytest.fixture()
def menu(premises):
    menu = Menu.objects.create(
        name='Main menu',
        premises=premises,
        is_default=True
    )
    return menu


@database_sync_to_async
@pytest.fixture(scope='session')
def vendor():
    user = get_user_model().objects.create_user(
        email='vendor@vendor.com',
        password='vendor',
        name="Mike Tayson"
    )
    user.groups.clear()
    user_group, _ = Group.objects.get_or_create(name="vendor")
    user.groups.add(user_group)
    user.save()
    return user

@database_sync_to_async
async def create_product(premises, menu, **params):
    defaults = {
            'name' : 'Cerveza',
            'description' : 'Really cold American Pale Ale',
            'price' : 9.99,
            'ingredients' : 'Hop, Water, Yeast',
            'estimated_creation_time' : 5.30,

    }
    defaults.update(params)

    return Product.objects.create(premises=premises, menu=menu, **defaults)


async def connect_and_create_order(user, status, premises, menu):
    product_one = create_product(premises=premises, menu=menu, name='Piwko')
    product_two = create_product(premises=premises, menu=menu, name='Cola')
    communicator = await auth_connect(user)
    
    await communicator.send_json_to({
        'type': 'create.order',
        'data': {
            'status': status,
            'customer': user.id,
            'premises': premises.id,
            'products': [
                product_one.id,
                product_two.id
            ]
        }
    })
    return communicator


async def connect_and_update_order(user, order, status, premises):
    communicator = await auth_connect(user)
    await communicator.send_json_to({
        'type': 'update.order',
        'data': {
            'id': f'{order.id}',
            'status': status,
            'vendor': user.id,
            # 'premises': premises.id
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

    async def test_customer_can_connect_to_server(self, settings, customer):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS
        communicator = await auth_connect(customer)
        await communicator.disconnect()

    async def test_customer_can_create_an_order(self, settings, customer, premises, menu):
        settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

        communicator = await connect_and_create_order(
            user=customer,
            status='REQUESTED',
            premises=premises, 
            menu=menu
        )

        response = await communicator.receive_json_from()
        data = response.get('data')
        print(data)

        assert 'REQUESTED' == data['status']

    # async def test_customer_is_added_to_order_groups_on_connect(self, settings, customer, premises):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     communicator = await connect_and_create_order(
    #         user=customer,
    #         status='REQUESTED',
    #         premises=premises,
    #         menu=self.menu
    #     )

    #     response = await communicator.receive_json_from()
    #     data = response.get('data')

    #     order_id = data['id']
    #     message = {
    #         'type': 'echo.message',
    #         'data': 'This is test message'
    #     }

    #     channel_layer = get_channel_layer()
    #     await channel_layer.group_send(order_id, message=message)

    #     response = await communicator.receive_json_from()

    #     assert message == response

    #     await communicator.disconnect()

    # async def test_customer_is_added_to_order_groups_on_init(self, settings, customer, premises):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     order = await create_order(
    #         status="REQUESTED",
    #         premises=premises,
    #         customer=customer,
    #         menu=self.menu
    #     )

    #     # user should be added to users groups
    #     communicator = await auth_connect(customer)

    #     message = {
    #         'type': 'echo.message',
    #         'data': 'This is test message'
    #     }

    #     channel_layer = get_channel_layer()
    #     await channel_layer.group_send(f'{order.id}', message=message)

    #     response = await communicator.receive_json_from()
    #     assert message == response

    #     await communicator.disconnect()

    # async def test_vendor_can_update_an_order(self, settings, premises, vendor, menu):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     order = await create_order(
    #         status="REQUESTED",
    #         premises=premises,
    #         menu=menu
    #     )

    #     communicator = await connect_and_update_order(
    #         user=vendor,
    #         order=order,
    #         status="IN_PROGRESS",
    #         premises=premises, 
    #     )

    #     response = await communicator.receive_json_from()

    #     data = response.get('data')

    #     assert data['status'] == 'IN_PROGRESS'
    #     assert data['customer'] == None
    #     assert data['vendor'].get('email') == vendor.email

    #     await communicator.disconnect()

    # async def test_vendor_is_added_to_order_group_on_update(self, settings, premises, vendor):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     order = await create_order(
    #         status="REQUESTED",
    #         premises=premises,
    #     )

    #     communicator = await connect_and_update_order(
    #         user=vendor,
    #         order=order,
    #         status=Order.IN_PROGRESS,
    #         premises=premises
    #     )

    #     response = await communicator.receive_json_from()
    #     data = response.get('data')

    #     order_id = data['id']
    #     message = {
    #         'type': 'echo.message',
    #         'data': 'This is test message'
    #     }

    #     channel_layer = get_channel_layer()

    #     await channel_layer.group_send(order_id, message=message)

    #     response = await communicator.receive_json_from()

    #     assert message == response

    #     await communicator.disconnect()

    # async def test_vendor_is_alerted_on_order_create(self, settings, customer, premises):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     channel_layer = get_channel_layer()
    #     await channel_layer.group_add(
    #         group='vendor',
    #         channel='test_channel'
    #     )

    #     communicator = await connect_and_create_order(
    #         user=customer,
    #         status="REQUESTED",
    #         premises=premises
    #     )

    #     response = await channel_layer.receive('test_channel')
    #     data = response.get('data')

    #     assert data['id'] != None
    #     assert customer.email == data['customer'].get('email')

    #     await communicator.disconnect()

    # async def test_customer_is_alerted_on_order_update(self, settings, premises, vendor):
    #     settings.CHANNEL_LAYERS = TEST_CHANNEL_LAYERS

    #     order = await create_order(
    #         status="REQUESTED",
    #         premises=premises
    #     )

    #     channel_layer = get_channel_layer()
    #     await channel_layer.group_add(
    #         group=f'{order.id}',
    #         channel='test_channel'
    #     )

    #     # json to server
    #     communicator = await connect_and_update_order(
    #         user=vendor,
    #         order=order,
    #         status=Order.IN_PROGRESS,
    #         premises=premises
    #     )

    #     response = await channel_layer.receive('test_channel')
    #     data = response.get('data')

    #     assert f'{order.id}' == data['id']
    #     assert vendor.email == data['vendor'].get('email')

    #     await communicator.disconnect()
