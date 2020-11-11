from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    """Createa a new user in the system"""
    serializer_class = UserSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retreive and return authenticated user"""
        return self.request.user
