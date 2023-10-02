from django.shortcuts import render,redirect,get_object_or_404
from cart.models import Cart,CartItems
from account.models import UserProfile
from orders.models import Order,OrderProduct,Payment
from store.models import Product,ProductImage,ProductSize
from django.db.models import Max
import razorpay
import os
from django.contrib import messages
import datetime
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def place_order(request):
    user=request.user
    if request.method == 'POST':
        address_id=request.POST.get('address')
        request.session["address_id"]=address_id
        try:
            address=UserProfile.objects.get(id=address_id)
        except UserProfile.DoesNotExist:
            if not address_id:
                messages.info(request,'Please select an address ')
                return redirect('checkout')
    cart_items=CartItems.objects.filter(cart__user=user)
    amount=0
    grand_total=0
    for cart_item in cart_items:
        grand_total+=cart_item.total_after_discount() 
    amount=grand_total*100
    context={
        'address':address,
        'amount':amount,
        }
    return render (request,'user/payment-confirmation.html',context)



@login_required
def checkout(request,total=0,quantity=0):
    user=request.user
#If the cart count is less than or equal to 0 , then redirect to store 
    cart_items=CartItems.objects.filter(cart__user=user)
    cart_count=cart_items.count()
    if cart_count<=0:
        return redirect('store')
    grand_total=0
    tax=0
    discount=0
    for cart_item in cart_items:
        total+=cart_item.sub_total()
        quantity+=cart_item.quantity
        tax+=cart_item.tax()
        if cart_item.cart.coupon:
            discount=cart_item.discount_amount()
        grand_total+=cart_item.total_after_discount() 
    address=UserProfile.objects.filter(user=user)
    context={
        'address':address,
        'cart_item':cart_items,
        'cart_count':cart_count,
        'total':total,
        'tax':tax,
        'discount':discount,
        'grand_total':grand_total
    }
    return render(request,'user/checkout.html',context)


@login_required
def confirmation(request,total=0):
    user=request.user
    address_id=request.session.get("address_id")
    order=None
    payment=None
    payment_method='razorpay'
    if request.method=='POST':
        payment_method=request.POST.get('pay-method')
    try:
        cart=Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return redirect('cart')
    cart_items=CartItems.objects.filter(cart__user=user)
    grand_total=0
    tax=0
    discount=0
    for cart_item in cart_items:
        total+=cart_item.sub_total()
        if cart.coupon:
            discount=cart_item.discount_amount()
        tax+=cart_item.tax()
    grand_total += total+tax-discount
    address=UserProfile.objects.get(id=address_id)
    if payment_method == 'razorpay':
        load_dotenv()
        client=razorpay.Client(auth=(os.getenv('RAZOR_PAY_KEY_ID'),os.getenv('KEY_SECRET')))
        # razorpay_payment=client.order.create({'amount':grand_total*100 , 'currency':'INR', 'payment_capture':1})
    order=Order.objects.create(user=user,address=address,order_total=grand_total,total=total,tax=tax,discount_price=discount)
    order.save()
    #generate order number
    yr=int(datetime.date.today().strftime('%Y'))
    dt=int(datetime.date.today().strftime('%d'))
    mt=int(datetime.date.today().strftime('%m'))
    d=datetime.date(yr,mt,dt)
    current_date=d.strftime("%Y%m%d")
    order_number=current_date+str(order.id)
    order.order_number=order_number
    order.save()
    for items in CartItems.objects.all():
        product=items.product
        product_stock=product.stock-items.quantity
        product.stock=product_stock
        product.save()
        image=ProductImage.objects.get(product_size=product)
        if product.offer_price==0:
            order_items=OrderProduct.objects.create(order=order,payment=payment,user=user,product=product,product_image=image,quantity=items.quantity,product_price=items.product.price,sub_total=items.sub_total(),tax=items.tax(),discount=items.discount_amount(),total=(items.sub_total()+items.tax()-items.discount_amount()))
        else:
            order_items=OrderProduct.objects.create(order=order,payment=payment,user=user,product=product,product_image=image,quantity=items.quantity,product_price=items.product.offer_price,sub_total=items.sub_total(),tax=items.tax(),discount=items.discount_amount(),total=(items.sub_total()+items.tax()-items.discount_amount()))        
        if payment_method=='cod':
            try:
                payment=Payment.objects.get(order=order)
            except Payment.DoesNotExist:
                payment=Payment.objects.create(user=user,payment_method=payment_method,order=order)
                payment.save()
                cart.delete()
        else:
            payment=Payment.objects.create(user=user,payment_method='razorpay',amount_paid=order.order_total,order=order,status='Completed')
            payment.save()
            order=Order.objects.get(id=payment.order_id)
            order.is_paid=True
            order.save()
            confirmed_payment=Payment.objects.get(order=order)
            order_items=OrderProduct.objects.filter(order=payment.order)
            for items in order_items:
                items.payment=confirmed_payment
                items.save()
            cart.delete()
    context={
        'order':order,
        'payment':payment,
        # 'razorpay_payment':razorpay_payment
    }
    return render(request,'user/confirmation.html',context)


@login_required
def my_order(request):
    user=request.user
    order=Order.objects.filter(user=user).order_by('-created_at')
    for item in order:
        quantity=0
        order_items=OrderProduct.objects.filter(order=item).order_by('-created_at')
        for i in order_items:
            quantity+=i.quantity        
    context={
        'user':user,
        'order':order,
        'order_items':order_items,
        'quantity':quantity,
    }
    return render(request,'user/my-order.html',context)


@login_required
def order_details(request,id):
    user=request.user
    order=Order.objects.get(pk=id)
    try:
        order_items=OrderProduct.objects.filter(order=id)
        # if order.status== 'Delivered':
        #     items=OrderProduct.objects.filter(order=order)
        #     for i in items:
        #         products=ProductSize.objects.filter(id=i.product_id)
        #         for product in products:
        #             product_stock=product.stock-i.quantity
        #             product.stock=product_stock
        #             product.save()
        payment=Payment.objects.get(order=id)
    except OrderProduct.DoesNotExist:
        
        order.delete()
        return redirect('my-order')
    context={
        'order_items':order_items,
        'order':order, 
        'payment':payment,  
        'user':user,  
    }
    return render(request,'user/order-details.html',context)

@login_required
def cancel_order(request,id):
    if request.method=='POST':
        order=Order.objects.get(pk=id)
        if order:
            order.status='Cancelled'
            order.save()
            order_items=OrderProduct.objects.filter(order=order)
            for items in order_items:
                product=items.product
                product.stock+=items.quantity
                product.save()
            messages.info(request,'You have cancelled an order')
    return redirect('my-order')
@login_required
def cancel_items(request,id):
    if request.method == 'POST':
        # item=[]
        order_item = OrderProduct.objects.get(pk=id)
        items=OrderProduct.objects.filter(order=order_item.order)
        if order_item:
            order=Order.objects.get(id=order_item.order_id)
            order_item.status = 'Cancelled'
            order_item.save()
            product= order_item.product
            product.stock += order_item.quantity
            product.save()
            if len(items)==1:
                order.status='Cancelled'
                order.save()
        return redirect('my-order')