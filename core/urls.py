from django.urls import path
from core import views

urlpatterns = [
    path('',views.index,name='index'),
    path('invoice/<int:id>',views.invoice,name='invoice')
]
