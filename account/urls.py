from django.urls import path
from account import views


urlpatterns = [
    path('register/',views.register,name='register'),
    path('signin/',views.signin,name='signin'),
    path('signin/otp-verify/<str:uid>/',views.otp_verify,name='otp-verify'),
    path('signout/',views.signout,name='signout'),
    path('verify_number/', views.verify_number, name='verify_number'),
    path('confirm_otp/', views.confirm_otp, name='confirm_otp'),
    path('change_password/', views.change_password, name='change_password'),
    path('profile/',views.profile,name='profile'),
    path('edit-profile/',views.edit_profile,name='edit-profile'),
    path('add-address/',views.add_address,name='add-address'),
    path('address/',views.address,name='address'),
    path('edit-address/<int:id>',views.edit_address,name='edit-address'),
    path('delete-address/<int:id>',views.delete_address,name='delete-address'),
    path('reset',views.reset_password,name='reset'),
    path('order-list',views.order_list,name='order-list'),
]


