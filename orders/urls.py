from django.urls import path
from orders import views


urlpatterns = [
    # path('place-order/',views.place_order,name='place-order'),
    path('checkout/',views.checkout,name='checkout'),
    path('create-order/',views.create_order,name='create-order'),
    # path('payment/',views.payment,name='payment'),
    path('razorpay_payment/',views.razorpay_payment,name='razorpay_payment'),
    path('confirmation/<int:id>',views.confirmation,name='confirmation'),
    path('my-order/',views.my_order,name='my-order'),
    path('order-details/<int:id>',views.order_details,name='order-details'),
    path('cancel_order/<int:id>',views.cancel_order,name='cancel_order'),
    path('cancel_items/<int:id>',views.cancel_items,name='cancel_items'),
]
