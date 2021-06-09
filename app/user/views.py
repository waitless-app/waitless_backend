from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer
from django.contrib.auth.models import Group


class CreateUserView(generics.CreateAPIView):
    """Createa a new user in the system"""
    serializer_class = UserSerializer
    def perform_create(self, serializer):
        instance = serializer.save()
        user_group, _ = Group.objects.get_or_create(name='customer')
        instance.groups.add(user_group)

class CreateVendorView(generics.CreateAPIView):
    """Createa a new user in the system"""
    serializer_class = UserSerializer

    # Add user created from this endpoint to vendor group
    def perform_create(self, serializer):
        instance = serializer.save()
        user_group, _ = Group.objects.get_or_create(name='vendor')
        instance.groups.add(user_group)

class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retreive and return authenticated user"""
        return self.request.user
