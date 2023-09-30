from django.urls import path
from adminpanel import views


urlpatterns = [
    path('admin-login/',views.admin_login,name='admin-login'),
    path('admin-dashboard/',views.admin_dashboard,name='admin-dashboard'),
    path('admin-logout/',views.admin_logout,name='admin-logout'),

    path('users/',views.userlist,name='users'),
    path('blockuser/<int:id>/',views.blockuser,name='blockuser'),
    path('unblockuser/<int:id>/',views.unblockuser,name='unblockuser'),

    path('categories/',views.categories,name='categories'),
    path('add-category/',views.add_category,name='add-category'),
    path('unblock-category/<int:id>/',views.unblock_category,name='unblock-category'),
    path('block-category/<int:id>/',views.block_category,name='block-category'),
    path('edit-category/<int:id>/',views.edit_category,name='edit-category'),
    # path('delete-category/<int:id>/',views.delete_category,name='delete-category'),

    path('product/',views.product,name='product'),
    path('add-product/',views.add_product,name='add-product'),
    path('edit-product/<int:id>/',views.edit_product,name='edit-product'),
    path('delete-product/<int:id>/',views.delete_product,name='delete-product'), 

    path('variants/<int:id>/',views.variant,name='variants'),
    path('add-variant/<int:id>/',views.add_variant,name='add-variant'),
    path('edit-variant/<int:variant_id>',views.edit_variant,name='edit-variant'),
    path('delete-variant/<int:id>/',views.delete_variant,name='delete-variant'),

    path('product-images/<int:id>/',views.product_image,name='product-images'),
    path('add-images/<int:id>/',views.add_image,name='add-images'),
    path('delete-images/<int:id>/',views.delete_image,name='delete-images'),

    path('coupon/',views.coupon,name='coupon'),
    path('add-coupon/',views.add_coupon,name='add-coupon'),
    path('edit-coupon/<int:id>',views.edit_coupon,name='edit-coupon'),
    path('delete-coupon/<int:id>',views.delete_coupon,name='delete-coupon'),

    path('sales-report/',views.sales_report,name='sales-report'),
    path('order/',views.order,name='order'),
    path('order_details/<int:id>',views.order_details,name='order_details'),
    path('update_order/<int:id>',views.update_order,name='update_order'),

    path('offers/',views.offers,name='offers'),
    path('add-offer/',views.add_offer,name='add-offer'),
    path('delete-offer/',views.delete_offer,name='delete-offer'),
 
]
