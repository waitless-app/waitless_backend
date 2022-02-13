from django.urls import path, include
from rest_framework.routers import DefaultRouter

from premises import views

router = DefaultRouter()
router.register('premises', views.PremisesViewSet)

app_name = 'premises'

urlpatterns = [
    path('', include(router.urls))

]
