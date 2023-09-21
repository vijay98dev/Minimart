from django.shortcuts import render
from store.models import Product,ProductImage,ProductSize
from orders.models import Order,Payment,OrderProduct
from django.utils import timezone


# Create your views here.
def index(request):
    product=ProductImage.objects.all()
    # try:
    #     offers=CategoryOffer.objects.filter(valid_to=timezone.now())
    #     offer_products=[]
    #     for offer in offers:
    #         products=offer.product.all()
    #         print(products,'111')
    #         offer_products.append({'offer':offer,'products':products})
    #     print(offer_products)
    # except CategoryOffer.DoesNotExist:
    #     pass

    context={
        'products':product,
        # 'offers':offers,
        # 'offer_products':offer_products,
    }
    return render(request,'user/index.html',context)


def invoice(request,id):
    user=request.user
    order=Order.objects.get(pk=id)
    print(order)
    order_items=OrderProduct.objects.filter(order=order)
    print(order_items)
    payment=Payment.objects.get(order=order)
    print(payment.id)
    context={
        'order':order,
        'order_items':order_items, 
        'payment':payment, 
    }
    return render(request,'user/invoice.html',context)