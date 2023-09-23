from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product,ProductImage,ProductSize
from cart.models import Cart,CartItems,Wishlist,Coupons,UserCoupons
from account.models import CustomUser,UserProfile
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
def cart(request,total=0,quantity=0,cart_items=None):
    user=request.user
    try:
        tax=0
        grand_total=0
        discount=0
        image=None
        if request.method=='POST':
            coupon_code=request.POST.get('coupon')
            try:
                coupon = Coupons.objects.get(coupon_code=coupon_code)
                # Check if the user already has this coupon
                if not UserCoupons.objects.filter(user=user, coupon=coupon).exists():
                    cart = Cart.objects.get(cart_id=_cart_id(request))
                    cart.coupon = coupon
                    cart.save()
                    UserCoupons.objects.create(user=user, coupon=coupon)
                    messages.success(request, 'Coupon added successfully')
                else:
                    messages.warning(request, 'You have already used this coupon')
            except Coupons.DoesNotExist:
                messages.warning(request, 'Please enter a valid coupon code')
        cart=Cart.objects.get(cart_id=_cart_id(request))

        # user_coupon=UserCoupons.objects.create(user=request.user,coupon=coupon)
        cart_items=CartItems.objects.filter(cart=cart).order_by('date_created')
        variants=ProductSize.objects.filter(id__in=cart_items.values('product'))
        image=ProductImage.objects.filter(product_size__in=variants.values('id'))
        for cart_item in cart_items:
            total+=cart_item.sub_total()
            quantity+=cart_item.quantity
            tax+=cart_item.tax()
            if cart.coupon: 
                discount=cart_item.discount_amount()
        
            grand_total=cart_item.total_after_discount()
        # if request.method=="POST":
        #     coupon=request.POST.get('coupon')
        #     coupon_obj=Coupons.objects.filter(coupon_code=coupon)
        #     if not coupon_obj.exists():
        #         messages.warning(request,'Please select a valid coupon code')
        #         return redirect('cart')
        #     if cart.coupon:
        #         messages.warning(request,'This coupon has already used')
        #         return redirect('cart')
        #     if grand_total<coupon_obj.minimum_amount:
        #         messages.warning(request,"Coupon doesn't satisfy the it's discrition")
        #         return redirect('cart')
        #     if coupon_obj.is_expired == True:
        #         messages.warning(request,'The coupon you have selected has been expired')
        #         return redirect('cart')
        #     if UserCoupons.objects.filter(user=request.user)==coupon_obj:
        #         messages.warning(request,'This coupon has already used')
        #         return redirect('cart')
        #     cart.coupon=coupon_obj
        #     cart.save()
            

    except ObjectDoesNotExist:
        pass
    context={
        'total':total,
        'quantity':quantity,
        'cart_items':cart_items,
        'tax':tax,
        'discount':discount,
        'grand_total':grand_total,
        'image':image
    }
    return render(request,'user/cart.html',context)

def _cart_id(request):
    cart=request.session.session_key
    if not cart:
        cart=request.session.create()
    return cart

def add_cart(request):
    # product=ProductSize.objects.get(id=product_id)
    size=None
    variable=None
    if request.method=='POST':
        size=request.POST.get('size')
        print(size)
        variable=ProductSize.objects.get(id=size)
        print(variable)
    product=variable.product
    print(product)
         
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request),user=request.user)
    cart.save()
    cart_item=CartItems.objects.filter(product=variable,cart=cart).exists()
    if cart_item:
        cart_item=CartItems.objects.get(product=variable,cart=cart)
        print(cart_item)
        # exis_list=[]
        # id=[]
        # for item in cart_item:
        #     existing_variable=item.product
        #     exis_list.append(existing_variable)
        #     id.append(item.id)
        # print(exis_list)
        # if size ==exis_list:
        #     index=exis_list.index(size)
        #     item_id=id[index]
        #     cart_item=CartItems.objects.get(product=product,id=item_id)
        if cart_item.quantity<variable.stock:
            cart_item.quantity += 1
        else:
            cart_item.quantity=variable.stock
            messages.error(request,'Product has reached its maximum stock')
        cart_item.save()
        # else:
        #     item=CartItems.objects.create(product=variable,quantity=1,cart=cart)
        #     item.save()
    else:
        cart_item=CartItems.objects.create(product=variable,quantity=1,cart=cart)
        cart_item.save()
    return redirect('cart')
def add_cart_items(request,product_id):
    variable=ProductSize.objects.get(id=product_id)
    try:
        cart=Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart=Cart.objects.create(cart_id=_cart_id(request),user=request.user)
    cart.save()
    cart_item=CartItems.objects.filter(product=variable,cart=cart).exists()
    if cart_item:
        cart_item=CartItems.objects.get(product=variable,cart=cart)
        print(cart_item)
        if cart_item.quantity<variable.stock:
            cart_item.quantity += 1
        else:
            cart_item.quantity=variable.stock
            messages.error(request,'Product has reached its maximum stock')
        cart_item.save()
    else:
        cart_item=CartItems.objects.create(product=variable,quantity=1,cart=cart)
        cart_item.save()
    return redirect('cart')
    # product=get_object_or_404(ProductSize, id=product_id)
    # cart=Cart.objects.get_or_create(user=request.user)
    # cart_item=CartItems.objects.get_or_create(cart=cart,product=product)
    # cart_item.quantity+=1
    # cart_item.save()
    # cart=CartItems.objects.all()
    # return redirect('cart')


def remove_cart(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(ProductSize,id=product_id)
    cart_item=CartItems.objects.get(product=product,cart=cart)
    if cart_item.quantity > 1:
        cart_item.quantity-=1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')

def remove_cart_items(request,product_id):
    cart=Cart.objects.get(cart_id=_cart_id(request))
    product=get_object_or_404(ProductSize,id=product_id)
    cart_item=CartItems.objects.get(product=product,cart=cart)
    cart_item.delete()
    return redirect('cart')



def wishlist(request):
    wishlist=Wishlist.objects.filter(user=request.user)
    products=Product.objects.filter(id__in=wishlist.values('product'))
    print(products)
    product_images = ProductImage.objects.filter(product__in=products).first()
    variant=ProductSize.objects.filter(product__in=products).first()
    print(variant)
    
    context={
        'wishlist':wishlist,  
        'variant':variant,  
        'product_image':product_images,
    }
    return render(request,'user/wishlist.html',context)

@login_required

def add_wishlist(request,id):
    user=request.user
    product=get_object_or_404(Product,id=id)
    wishlist=Wishlist.objects.filter(user=user)
    if not wishlist.filter(user=user,product=product).exists():
        Wishlist.objects.create(user=user,product=product)
        messages.success(request,'Product added to your wishlist')
        return redirect('wishlist')

    return redirect('product_details',category_slug=product.product.category.slug,product_slug=product.slug)


@login_required
def remove_wishlist(request,id):
    user=request.user
    product=get_object_or_404(Product,id=id)
    wishlist=Wishlist.objects.get(user=user,product=product)
    wishlist.delete()
    messages.info(request,'Product removed from wishlist')
    return redirect ('wishlist')


@login_required
def coupon_list(request):
    user=request.user
    user_coupons=UserCoupons.objects.filter(user=user)
    unused_coupons = Coupons.objects.exclude(usercoupons__is_used=True)

    context={
        'unused_coupons':unused_coupons,
        'user_coupons':user_coupons

    }
    return render(request,'user/coupon-list.html',context)