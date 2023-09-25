from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,ProductImage,ProductSize
from django.db.models import Q
from category.models import Category,CategoryOffer
from django.http import Http404
from cart.models import Cart,CartItems,Wishlist
from cart.views import _cart_id
# Create your views here.

def store(request,category_slug=None):
    categories=Category.objects.all()
    products=None
    product_counts=Product.objects.all().count()
    if category_slug is not None:
        category=get_object_or_404(Category,slug=category_slug)
        products=Product.objects.all().filter(category__slug=category_slug,is_available=True)
    else:
        products=Product.objects.filter(is_available=True) 
    context={
        'product':products,
        'product_counts':product_counts,
        'categories':categories,
    }
    return render(request,'user/store.html',context)


def product_details(request,category_slug,product_slug):
    try:
        single_product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        single_product_details=ProductSize.objects.filter(product=single_product).first()
        single_product_image=ProductImage.objects.filter(product=single_product).first()
        size=ProductSize.objects.filter(product=single_product).order_by('created_date')
        # in_cart=CartItems.objects.filter(cart__cart_id=_cart_id(request),product=size).exists()
        in_offer=CategoryOffer.objects.filter(is_active=True).exists()
        in_whishlist=Wishlist.objects.filter(user=request.user,product=single_product).exists()
    except ProductImage.DoesNotExist:
        raise Http404("Product not found")
    context={
        'single_product':single_product,
        'product':single_product_details,
        'image':single_product_image,
        'size':size,
        'in_whishlist':in_whishlist,
    }
    return render(request,'user/product_details.html', context)


def search(request):

    if 'keyword' in request.GET:
        keyword=request.GET['keyword']
        if keyword:
            product=ProductImage.objects.filter(Q(product__product_name__icontains=keyword) | Q(product__description__icontains=keyword) | Q(product__category__category_name__icontains=keyword) | Q(product_size__price__icontains=keyword))
            
        products=Product.objects.filter(id__in=product.values('product'))
        product_count=products.count()
        print(products)
        # category=Category.objects.get(id__in=products)
        # image=ProductImage.objects.filter(product__in=products)
        context={
            'products':products, 
            'product_counts':product_count, 
            # 'categories':category, 
        }
    return render(request,'user/search.html',context)

