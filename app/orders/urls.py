from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('', views.OrderView.as_view(
        {'get': 'list'}), name='order_list'),
    path('<uuid:pk>', views.OrderView.as_view(
        {'get': 'retrieve'}), name='order_detail'),
    path('confirm_pickup_code', views.confirm_pickup_code, name='order_detail')

]
