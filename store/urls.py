from django.urls import path
from store import views

urlpatterns = [
    path('store/',views.store,name='store'),
    path('store/<category_slug>/',views.store,name='product_by_slug'),
    path('store/<category_slug>/<product_slug>/',views.product_details,name='product_details'),
    path('search/',views.search,name='search'),
]
