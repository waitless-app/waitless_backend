import uuid

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.conf import settings
from django.shortcuts import reverse


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

    # traktuje groip to jako pole
    @property
    def group(self):
        groups = self.groups.all()
        return groups[0].name if groups else None


class Premises(models.Model):
    """Premises object"""
    # owner = models.ForeignKey(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE
    # )
    name = models.CharField(max_length=255)
    image_url = models.CharField(max_length=255)
    city = models.CharField(max_length=255, blank=True)

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
    vendor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='orders_as_vendor'
    )
    premises = models.ForeignKey(
        Premises,
        on_delete=models.CASCADE,
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    ready_time = models.DateTimeField(null=True)
    collected_time = models.DateTimeField(null=True)
    status = models.CharField(
        max_length=20, choices=STATUSES, default=REQUESTED)
    product = models.CharField(max_length=255, default='Cerveza')
    order_comment = models.TextField(max_length=500, null=True)

    def __str__(self):
        return f'{self.id, self.premises}'

    def get_absolute_url(self):
        return reverse('order:order_detail', kwargs={'order_id': self.id})
