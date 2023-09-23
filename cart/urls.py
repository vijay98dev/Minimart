from django.urls import path
from cart import views


urlpatterns = [
    path('cart/',views.cart,name='cart'),
    path('add_cart/',views.add_cart,name='add_cart'),
    path('add_cart_items/<int:product_id>/',views.add_cart_items,name='add_cart_items'),
    path('remove_cart/<int:product_id>/',views.remove_cart,name='remove_cart'),
    path('remove_cart_items/<int:product_id>/',views.remove_cart_items,name='remove_cart_items'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('add-wishlist/<int:id>/',views.add_wishlist,name='add-wishlist'),
    path('remove-wishlist/<int:id>/',views.remove_wishlist,name='remove-wishlist'),

    path('coupon-list/',views.coupon_list,name='coupon-list'),

]
