from django.shortcuts import render
from store.models import Product,ProductImage,ProductSize
from category.models import CategoryOffer,Category
from orders.models import Order,Payment,OrderProduct
from django.utils import timezone
from django.db.models import Q

# Create your views here.
def index(request):
    user=request.user
    offer_products=None
    product=Product.objects.all().filter(Q(is_available=True) &Q(offer_applied=False))
    try:
        offers=CategoryOffer.objects.all().filter(is_active=True)
        # Loop through all the offers present
        for offer in offers:
            category_offer=offer.category
            offer_discount=offer.discount_percentage
            # products that falls under the offer
            offer_products=Product.objects.filter(category=category_offer)
            for products in offer_products:
                products.offer_applied=True
                products.save()
                variant=ProductSize.objects.filter(product=products)
                for items in variant:
                    items.offer_price = items.price - (items.price * offer_discount / 100)
                    items.save()
        in_offer=CategoryOffer.objects.filter(is_active=True).exists()
    except CategoryOffer.DoesNotExist:
        pass

    context={
        'product':product,
        'offer_product':offer_products,
        'in_offer':in_offer,
    }
    return render(request,'user/index.html',context)


def invoice(request,id):
    user=request.user
    order=Order.objects.get(pk=id)
    order_items=OrderProduct.objects.filter(order=order)
    payment=Payment.objects.get(order=order)
    context={
        'user':user,
        'order':order,
        'order_items':order_items, 
        'payment':payment, 
    }
    return render(request,'user/invoice.html',context)