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


# Create your views here.


# def place_order(request):
#     order=Order.objects.get(user=request.user,is_paid=False)
#     if request.method =="POST":
#         payment_method=request.POST.get('pay-method')
    
#     context={
#         }
#     return render (request,'user/payment-confirmation.html',context)




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
    # client=razorpay.Client(auth=(os.environ['razor_pay_key_id'],os.environ['key_secret'])
    # payment=client.order.create({'amount'})
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


def confirmation(request):
    order_id=request.GET.get('razorpay_order_id')
    payment_id=request.GET.get('razorpay_payment_id')
    signature=request.GET.get('razorpay_signature')
    payment=Payment.objects.get(razor_pay_order_id=order_id)
    payment.razor_pay_payment_id=payment_id
    payment.razor_pay_payment_signature=signature
    payment.status='Completed'
    payment.save()
    order=Order.objects.get(id=payment.order_id)
    order.is_paid=True
    order.save()
    confirmed_payment=Payment.objects.get(razor_pay_order_id=order_id)
    order_items=OrderProduct.objects.filter(order=payment.order_id)
    for items in order_items:
        items.payment=confirmed_payment
        items.save()
    context={
        'order':order
    }
    return render (request,'user/confirmation.html',context)

def create_order(request,total=0):
    user=request.user
    address_id=None
    order=None
    payment=None
    payment_method='razorpay'
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
        
    if request.method == 'POST':
        if 'checkout_submit' in request.POST:
            address_id=request.POST.get('address')
            try:
                address=UserProfile.objects.get(id=address_id)
            except UserProfile.DoesNotExist:
                if not address_id:
                    messages.info(request,'Please select an address ')
                    return redirect('checkout')
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
                image=ProductImage.objects.get(product_size=product)
                order_items=OrderProduct.objects.create(order=order,payment=payment,user=user,product=product,product_image=image,quantity=items.quantity,product_price=items.product.price,sub_total=items.sub_total(),tax=items.tax(),discount=items.discount_amount(),total=(items.sub_total()+items.tax()-items.discount_amount()))
        # if 'payment_submit' in request.POST:
        #     print("else payment")
        #     payment_method=request.POST.get('pay-method')
        if 'payment_submit' in request.POST:
            payment_method='razorpay'
            order = Order.objects.filter(user=user).order_by('-created_at').first()
            
            payment_method=request.POST.get('pay-method')
            if payment_method=='cod':
                payment=Payment.objects.create(user=user,payment_method=payment_method,order=order)
                payment.save()
                payment=Payment.objects.get(order=order)

                return redirect('confirmation-cod' ,order.id)
    print('11111111111111111111111111111111111111111111111111111111')
    try:
        payment=Payment.objects.get(order=order)
        print('2222222222222222222222222')
    except Payment.DoesNotExist:
        print('2222222222222222222222222')
        load_dotenv()
        client=razorpay.Client(auth=(os.getenv('RAZOR_PAY_KEY_ID'),os.getenv('KEY_SECRET')))
        razorpay_payment=client.order.create({'amount':grand_total*100 , 'currency':'INR', 'payment_capture':1})
        print(razorpay_payment)
        payment=Payment.objects.create(user=user,payment_method='razorpay',amount_paid=grand_total,razor_pay_order_id=razorpay_payment['id'],order=order)
        print(payment.id)
        payment.save()
# payment=Payment(user=user,)
    # cart=Cart.objects.get(user=request.user)
    # cart_items=CartItems.objects.filter(cart=cart)
    
    # address=get_object_or_404(UserProfile,id=address_id)
    amount=grand_total*100
    cart.delete()
    context={
        'order':order,
        'payment':payment,
        'amount':amount,
        'razorpay_payment':razorpay_payment
    }
    return render(request,'user/payment-confirmation.html',context)


def confirmation_cod(request,id):
    order=Order.objects.get(pk=id)
    context={
        'order':order
    }
    return render(request,'user/confirmation-cod.html',context)


def my_order(request):
    user=request.user
    order=Order.objects.filter(user=user).order_by('-created_at')
    order_items=OrderProduct.objects.filter(order__in=order).order_by('-created_at')
    quantity=0
    for i in order_items:
        quantity+=i.quantity
    image=OrderProduct.objects.filter(order__in=order).order_by('-created_at').first()
    context={
        'user':user,
        'order':order,
        'order_items':order_items,
        'quantity':quantity,
        'image':image,
    }
    return render(request,'user/my-order.html',context)

def order_details(request,id):
    order=Order.objects.get(pk=id)
    try:
        order_items=OrderProduct.objects.filter(order=id)
        
        payment=Payment.objects.get(order=id)
    except OrderProduct.DoesNotExist:
        order.delete()
        return redirect('my-order')
    context={
        'order_items':order_items,
        'order':order, 
        'payment':payment, 
    }
    return render(request,'user/order-details.html',context)

def cancel_order(request,id):
    if request.method=='POST':
        order=Order.objects.get(pk=id)
        if order:
            order.status='Cancelled'
            order.save()
            order_items=OrderProduct.objects.filter(order__in=order)
            for items in order_items:
                product=items.product
                product.stock+=items.quantity
                product.save()
            messages.info(request,'You have cancelled an order')
    return redirect('my-order')

def cancel_items(request,id):
    if request.method == 'POST':
        order_item = OrderProduct.objects.get(pk=id)
        if order_item:
            order_item.order.status = 'Cancelled'
            order_item.save()
            product = order_item.product
            product.stock += order_item.quantity
            product.save()
        return redirect('myorders')