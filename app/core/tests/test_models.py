from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models

def sample_user(email='sample@user.pl', password='testpassword' ):
    ### Crreate sample user"""
    return get_user_model().objects.create_user(email, password) 

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
        """Test the recipce string represent"""
        recipe = models.Premises.objects.create(
            user=sample_user(),
            name='Szot',
            image_url='https://media-cdn.tripadvisor.com/media/photo-s/16/4c/a7/39/a-o-to-i-nasz-steampunkowy.jpg',
            city='Gdynia',
        )

        self.assertEqual(str(recipe), recipe.name)