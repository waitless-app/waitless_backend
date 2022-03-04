from django.urls import path, include
from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('menu', views.MenuViewset)
router.register('products', views.ProductViewset)

app_name = 'product'

urlpatterns = [
    path('', include(router.urls))
]
