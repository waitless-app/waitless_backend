from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderView.as_view(
        {'get': 'list', 'post': 'create'}), name='order_list'),
]
