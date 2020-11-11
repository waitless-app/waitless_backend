from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='sample@user.pl', password='testpassword'):
    # Crreate sample user"""
    return get_user_model().objects.create_user(email, password)


def sample_premises(
    owner,
    name='Szot',
    image_url='https://via.placeholder.com/350x150',
    city='Gdynia'
):

    return models.Premises.objects.create(
        name=name, 
        image_url=image_url,
        city=city,
        owner=owner
    )

def sample_menu(
    name='Master menu',
    is_default=True
):
    premises=sample_premises(owner = sample_user(email='owner@onboard.io'))
    return models.Menu.objects.create(name=name, premises=premises, is_default=is_default)
def sample_product(
      name = 'AleBrowar Easy Pale Ale DDH Comet',
        description = 'Very tasty cold drink',
        is_active=True,
        price = 9.99,
        ingredients = 'Hop, Water, Yeast',
        estimated_creation_time = 5.10
):
    owner = sample_user(email='product@onboard.io')
    premises=sample_premises(owner=owner)
    menu = sample_menu()
    return models.Product.objects.create(
            name=name,
            description=description,
            is_active=is_active,
            price=price,
            ingredients=ingredients,
            estimated_creation_time=estimated_creation_time,
            menu=menu,
            premises=premises,
        )
class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is succesful"""
        email = 'test@test.com'
        password = 'testpassowrd123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Terst the email for a new user is normalized"""
        email = 'sample@SAMPLE.test'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_empty_user_raises_error(self):
        """Test that no username raises an error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        user = get_user_model().objects.create_superuser(
            'test@test.pl',
            'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_new_superuser_with_name(self):
        """Test to create user with name"""
        email = 'test@test.com'
        password = 'testpassowrd123'
        name = 'Mike'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            name=name,
        )
        self.assertEqual(user.name, name)

    def test_premises_str(self):
        """Test the premises string represent"""
        premises = models.Premises.objects.create(
            name='Szot',
            image_url='https://via.placeholder.com/350x150',
            city='Gdynia',
            owner= sample_user()
        )

        self.assertEqual(str(premises), premises.name)

    def test_orders_str(self):
        """Test orders string represent"""
        owner = sample_user(email='owner@onboard.io')
        order = models.Order.objects.create(
            status="REQUESTED",
            premises=sample_premises(owner=owner)
        )
        self.assertEqual(str(order), str(order.id))

    def test_create_menu(self):
        name = 'Master Menu'
        owner = sample_user(email='owner@onboard.io')
        premises = sample_premises(owner=owner)

        menu = models.Menu.objects.create(
            name=name,
            premises = premises
        )
        self.assertEqual(menu.name, name)

    def test_menu_str(self):
        menu = sample_menu()
        self.assertEqual(str(menu), menu.name)


    def test_product_create(self):
        name = 'AleBrowar Easy Pale Ale DDH Comet'
        description = 'Very tasty cold drink'
        is_active=True
        price = 9.99
        ingredients = 'Hop, Water, Yeast'
        estimated_creation_time = 5.10
        menu = sample_menu()
        owner = sample_user(email='owner2@onboard.io')
        premises = sample_premises(owner=owner)
     
        

        product = models.Product.objects.create(
            name=name,
            description=description,
            is_active=is_active,
            price=price,
            ingredients=ingredients,
            estimated_creation_time=estimated_creation_time,
            menu=menu,
            premises=premises,
        )
        self.assertEqual(product.name, name)
    def test_product_str(self):
    # Sample product for str test
    # Sample 'product' added to 'menu' with 'premises' added by 'owner'  
        product = sample_product(name='Cold Vodka')

        self.assertEqual(str(product), product.name)

    def test_orderproduct_create(self):
        owner = sample_user(email='owner1@onboard.io')
        order = models.Order.objects.create(
            status="REQUESTED",
            premises=sample_premises(owner=owner)
        )
        product = sample_product()
        quantity = 2
        orderproduct = models.OrderProduct.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )
        self.assertEqual(orderproduct.order, order)