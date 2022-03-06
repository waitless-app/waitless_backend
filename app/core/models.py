import random
import uuid

from django.db import models
from django.contrib.gis.db.models import PointField
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.shortcuts import reverse
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """Creates and saves a new user """
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Creates and saves a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that supports using email instead of username"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def group(self):
        groups = self.groups.all()
        return groups[0].name if groups else None


class Tag(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Premises(models.Model):
    """Premises object"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_premises'
    )
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to='product')
    city = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
    description = models.TextField(null=True)
    country = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    postcode = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    location = PointField(null=False, blank=False,
                          srid=4326, verbose_name='Location')
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_completed_orders(self):
        return self.orders_as_premises.filter(status="COMPLETED").count()

    def get_active_orders(self):
        return self.orders_as_premises.exclude(status="COMPLETED").count()

    def get_month_income(self):
        import calendar

        now = timezone.now()

        start_date = now.replace(
            day=calendar.monthrange(now.year, now.month)[0])
        end_date = now.replace(
            day=calendar.monthrange(now.year, now.month)[1])

        order_total_list = [order.total_cost for order in
                            self.orders_as_premises.filter(
                                created__gte=start_date,
                                created__lte=end_date)]
        return sum(map(float, order_total_list))

    def get_today_income(self):
        today_start = timezone.now().replace(hour=0, minute=0, second=0)
        today_end = timezone.now().replace(hour=23, minute=59, second=59)

        order_total_list = [order.total_cost for order in
                            self.orders_as_premises.filter(
                                created__gte=today_start,
                                created__lte=today_end)]

        return sum(map(float, order_total_list))


class Menu(models.Model):
    name = models.CharField(max_length=255)
    premises = models.ForeignKey(Premises, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class ProductCategory(models.Model):
    name = models.CharField(max_length=255)
    premises = models.ForeignKey(
        Premises, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    ingredients = models.CharField(max_length=255)
    estimated_creation_time = models.DecimalField(
        max_digits=5, decimal_places=2)
    menu = models.ForeignKey(Menu, models.SET_NULL,
                             blank=True, null=True, related_name="products")
    premises = models.ForeignKey(Premises, on_delete=models.CASCADE)
    image = models.FileField(upload_to='product')
    group = models.ForeignKey(
        ProductCategory, default=None, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Order(models.Model):
    REQUESTED = 'REQUESTED'
    ACCEPTED = 'ACCEPTED'
    DECLINED = 'DECLINED'
    STARTED = 'STARTED'
    IN_PROGRESS = "IN_PROGRESS"
    READY = "READY"
    COMPLETED = "COMPLETED"
    STATUSES = (
        (REQUESTED, REQUESTED),
        (ACCEPTED, ACCEPTED),
        (DECLINED, DECLINED),
        (STARTED, STARTED),
        (IN_PROGRESS, IN_PROGRESS),
        (READY, READY),
        (COMPLETED, COMPLETED),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='orders_as_customer'
    )
    premises = models.ForeignKey(
        Premises,
        on_delete=models.CASCADE,
        related_name='orders_as_premises'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ready_time = models.DateTimeField(null=True)
    collected_time = models.DateTimeField(null=True)
    accept_time = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=20, choices=STATUSES, default=REQUESTED)
    order_comment = models.TextField(max_length=500, null=True)
    pickup_code = models.CharField(
        max_length=10,
        null=True,
        editable=False,
        unique=True,
        default=None
    )

    @property
    def total_cost(self):
        total = 0
        for order_product in self.order_products.all():
            total += order_product.product.price * order_product.quantity
        # Cannot serialize decimal out of the box
        return str(total)

    def __str__(self):
        return f'{self.id}'

    def get_absolute_url(self):
        return reverse('order:order_detail', kwargs={'order_id': self.id})

    def generate_order_pickup_code(self):
        self.pickup_code = str(random.randint(100000, 999999))

    def clear_order_pickup_code(self):
        self.pickup_code = self._meta.get_field('pickup_code').get_default()


class OrderProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_products")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.id}'

    class Meta:
        unique_together = ('order', 'product')
