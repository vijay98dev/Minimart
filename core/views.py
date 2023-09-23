from django.shortcuts import render
from store.models import Product,ProductImage,ProductSize
from orders.models import Order,Payment,OrderProduct
from django.utils import timezone


# Create your views here.
def index(request):
    product=Product.objects.all().filter(is_available=True)
    variant=ProductSize.objects.filter(product__in=product).first()
    image=ProductImage.objects.filter(product__in=product).first()
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
        'variant':variant,
        'image':image,
        # 'offers':offers,
        # 'offer_products':offer_products,
    }
    return render(request,'user/index.html',context)


def invoice(request,id):
    user=request.user
    order=Order.objects.get(pk=id)
    order_items=OrderProduct.objects.filter(order=order)
    payment=Payment.objects.get(order=order)
    context={
        'order':order,
        'order_items':order_items, 
        'payment':payment, 
    }
    return render(request,'user/invoice.html',context)