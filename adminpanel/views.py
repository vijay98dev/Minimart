from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.urls import reverse
from account.models import CustomUser
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from account.models import CustomUser
from category.models import Category,CategoryOffer
from store.models import Product,ProductImage,ProductSize
from django.utils.text import slugify
from orders.models import Order,OrderProduct,Payment
from cart.models import Coupons,UserCoupons
from datetime import timedelta, datetime ,date
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models import Q



# Create your views here.

def admin_login(request):
    try:
        if request.user.is_authenticated:
            return redirect('admin-dashboard')
        if request.method=='POST':
            email=request.POST["email"]
            password=request.POST['password']
            user=CustomUser.objects.filter(email=email)
            if not user.exists():
                messages.success(request,'Account not found')
                return redirect('admin-login')
            user=authenticate(email=email,password=password)
            if user and user.is_superuser:
                login(request,user)
                return redirect('admin-dashboard')
            
            messages.error(request,'Invalid Password')
            return redirect('admin-login')

        return render(request,'admin/admin-login.html')
    except Exception as e:
        print(e)
    return render(request,'admin/admin-login.html')



def admin_dashboard(request):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Adjust the number of days as needed

    # Query the database to get daily order counts for the last five days
    daily_order_counts = (
        Order.objects
        .filter(created_at__range=(start_date, end_date))
        .values('created_at__date')
        .annotate(order_count=Count('id'))
        .order_by('created_at__date')
    )
    orders= Order.objects.all().order_by('-created_at')[:10]
    # Extract dates and counts for the chart
    dates = [entry['created_at__date'].strftime('%Y-%m-%d') for entry in daily_order_counts]
    counts = [entry['order_count'] for entry in daily_order_counts]
    order=Order.objects.all()
    order_count=order.count()
    today = datetime.now()
    month=end_date-timedelta(days=30)
    total=(
    Order.objects.filter(created_at__range=(month, today)).aggregate(total_order_total=Sum('order_total')))['total_order_total']

    context = {
        'dates': dates,
        'counts': counts, 
        'orders': orders, 
        'order_count': order_count, 
        'total': total, 
    }

    return render(request, 'admin/admin_dashboard.html', context)

@login_required(login_url='admin-login')
def admin_logout(request):
    logout(request)
    messages.success(request,'Logout successful')
    return redirect('admin-login')

def userlist(request):
    user=CustomUser.objects.all().order_by('date_joined')
    context={
        'users':user
    }
    return render (request,'admin/userlist.html',context)


def blockuser(request,id):
    user=get_object_or_404(CustomUser,pk=id)
    
    # user_id=request.GET.get('id')
    # user=CustomUser.objects.get(pk=user_id)
    user.is_active=False
    user.save()
    return redirect('users')

def unblockuser(request,id):
    user=get_object_or_404(CustomUser,pk=id)
    # user_id=request.GET.get('id')
    # user=CustomUser.objects.get(pk=user_id)
    user.is_active=True
    user.save()
    return redirect('users')

def categories(request):
    category=Category.objects.all()
    context={
        'categories':category
    }
    return render(request,'admin/category.html',context)

def unblock_category(request,id):
    category=get_object_or_404(Category,pk=id)
    category.unblock()
    category.save
    return redirect('categories')

def block_category(request,id):
    category=get_object_or_404(Category,pk=id)
    category.block()
    category.save
    return redirect('categories')

def add_category(request):
    if request.method=='POST':
        category_name=request.POST['category_name']
        description=request.POST['description']
        slug=slugify(category_name)
        if Category.objects.filter(category_name=category_name).exists():
            messages.error(request,'Category already exist')
            return redirect ('add-category')
        else:
            category = Category(category_name=category_name,description=description,slug=slug)
            category.save()
        return redirect('categories')
    return render(request, "admin/add-category.html")


def edit_category(request, id):
    categories = get_object_or_404(Category, pk=id)
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        description = request.POST.get('description')
        slug = slugify(category_name)
        
        # Check if category_name has changed and if it's not already taken
        if categories.category_name != category_name and Category.objects.filter(category_name=category_name).exists():
            messages.error(request, 'Category name already exists')
        else:
            categories.category_name = category_name
            categories.description = description
            categories.slug = slug
            categories.save()
            messages.success(request, 'Category changed successfully')
        
        return redirect('categories')
    
    context = {'category': categories}
    return render(request, 'admin/edit-category.html', context)

def product(request):
    product=Product.objects.all().order_by('id')
    context={
        'products':product
    }
    return render(request,'admin/product.html',context)


def add_product(request):
    if request.method=='POST':
        product_name=request.POST.get('product_name')
        description=request.POST.get('description')
        size=request.POST.get('size')
        price=request.POST.get('price')
        uploaded_image=request.FILES.getlist('image') 
        stock=request.POST.get('stock')  
        category_id=request.POST.get('category')  
        if Product.objects.filter(product_name=product_name).exists():
            messages.error(request,'Product name is already exists')
            return redirect('add-product')
        else:
            selected_category=get_object_or_404(Category,id=category_id)
            if size:
                size=float(size)
            product = Product.objects.create(product_name=product_name,description=description,category=selected_category)
            size_product=ProductSize.objects.create(price=price,stock=stock,product_size=size,product=product)
            for images in uploaded_image:
                images=ProductImage.objects.create(product_image=images,product=product,product_size=size_product)
            messages.success(request,'Product added successfully')
            return redirect('product')
    categories=Category.objects.all()
    context={
        'categories':categories
    }
    return render(request,'admin/add-product.html',context)


def delete_product(request,id):
    product=get_object_or_404(Product,id=id)
    product.soft_delete()
    return redirect('product')

def edit_product(request,id):
    product=Product.objects.get(pk=id)
    if request.method=='POST':
        description=request.POST.get('description')
        product.description=description
        product.save()
        return redirect('product')
    categories=Category.objects.all()
    context={
        'categories':categories,
        'products':product
    }
    return render(request,'admin/edit-product.html',context)

def variant(request,id):
    variant= ProductSize.objects.filter(product=id).order_by('id')
    product=get_object_or_404(Product,pk=id)

    context={
        'variants':variant,
        'product':product
    }
    return render(request,'admin/variants.html',context)

def add_variant(request,id):    
    product=get_object_or_404(Product,pk=id)
    if request.method=='POST':
        size= float(request.POST.get('size'))
        price=float(request.POST.get('price'))
        stock=int(request.POST.get('stock'))
        existing_size=ProductSize.objects.filter(product=product, product_size=size).first()
        if existing_size:
            messages.error(request,'Size already exists')
            # return redirect(reverse('add-variant',args=[product.id]))
        else:
            size_product=ProductSize.objects.create(price=price,stock=stock,product_size=size,product=product)
            messages.success(request,'Variant added successfully')
            return redirect(reverse('add-variant',args=[product.id]))
    context={
        'product':product

    }
    return render(request,'admin/add-variant.html',context)

def edit_variant(request,variant_id):
    variant=ProductSize.objects.get(id=variant_id)
    product=variant.product
    if request.method =='POST':
        stock=request.POST.get('stock')
        price=request.POST.get('price')
        variant.stock=stock
        variant.price=price
        variant.save()
        messages.success(request,'Variant changed successfully')
        return redirect('variants' ,product.id)

    
    context={'variants':variant}
    return render(request,'admin/edit-variant.html',context)

def delete_variant(request,id):
    variant=get_object_or_404(ProductSize,pk=id)
    variant.soft_delete()
    return redirect('product')

def product_image(request,id):
    images=ProductImage.objects.filter(product_size=id).order_by('id')
    product=ProductSize.objects.get(id=id)
    context={
        'image':images,
        'product':product,
    }
    return render(request,'admin/product-image.html',context)

def add_image(request,id):
    variant=ProductSize.objects.get(pk=id)
    product=variant.product
    if request.method=='POST':
        uploaded_image=request.FILES.getlist('image')
        for images in uploaded_image:
            images=ProductImage.objects.create(product_image=images,product_size=variant,product=product)
        messages.success(request,'Product Image added successfully')
        return redirect('product-images',variant.id)
    image=get_object_or_404(ProductSize,pk=id)
    context={
        'images':image,
        'variant':variant
    }
    return render(request,'admin/add-productimage.html',context)

# def edit_image(request,id):
#     pass

def delete_image(request,id):
    image=ProductImage.objects.get(pk=id)
    variant=image.product_size
    image.delete()
    return redirect('product')



def order_details(request,id):
    order = get_object_or_404(Order, id=id)
    product = OrderProduct.objects.filter(order=order)
    order_item=OrderProduct.objects.all()
    order_status_choices=OrderProduct.ORDER_STATUS
    context={
        'products':product,
        'order':order,
        'order_item':order_item,
        'order_status_choices':order_status_choices,
        }
    return render(request,'admin/admin_order_details.html',context)



def sales_report(request):
    if request.method=='POST':
        from_str=request.POST.get('start_date')
        to_str=request.POST.get('end_date')
        end_date=datetime.now(timezone.utc)
        from_date=datetime.strptime(from_str,"%m%d%Y").strftime("%Y-%m%d %H:%M:%S")
        to_date=datetime.strptime(to_str,"%m%d%Y").strftime("%Y-%m%d %H:%M:%S")
    else:
        from_date=None
        to_date=None
    end_date=datetime.now(timezone.utc)
    week_date=datetime.now(timezone.utc)-timedelta(days=7)
    order_items=OrderProduct.objects.filter(created_at__range=['from_date','to_date'])
    for items in order_items:
        sub_total=items.product_price*items.quantity
        tax=(5*sub_total)/100
        total=sub_total+tax
    context={
        'order_items':order_items,
        'sub_total':sub_total,
        'tax':tax,
        'total':total,
    }
    return render(request,'admin/sales-report.html',context)


def order(request):
    orders=Order.objects.all().order_by('-created_at')
    order_status_choices=Order.ORDER_STATUS
    context={
        'orders':orders,
        'order_status_choices':order_status_choices
    }
    return render(request,'admin/orders.html',context)

def update_order(request,id):
    order=Order.objects.get(pk=id)
    order_items=OrderProduct.objects.filter(order=order)
    payment=Payment.objects.get(order=order)
    if request.method=='POST':
        status=request.POST.get('order_status')
    order.status=status
    order.save()
    
    if payment.payment_method=='cod':
        if order.status=='Delivered':
            order.is_paid=True
            order.save()
        else:
            order.is_paid=False
            order.save()
    for items in order_items:
        items.status=status
        items.payment=payment
        items.save()
    return redirect('order')


def coupon(request):
    coupons=Coupons.objects.all()
    context={
        'coupons':coupons
    }
    return render(request,'admin/coupon.html',context)

def add_coupon(request):
    coupon=Coupons.objects.all()
    if request.method=='POST':
        coupon_code=request.POST.get('coupon_code')
        description=request.POST.get('description')
        minimum_amount=request.POST.get('minimum_amount')
        discount=request.POST.get('discount')
        valid_from=request.POST.get('valid_from')
        valid_to=request.POST.get('valid_to')
        try:
            invalid_coupon=Coupons.objects.get(coupon_code=coupon_code)
            messages.error(request,'Coupon Code already exist')
            return redirect('add-coupon')
        except Coupons.DoesNotExist:
            coupon=Coupons.objects.create(coupon_code=coupon_code,description=description,minimum_amount=minimum_amount,discount=discount,valid_from=valid_from,valid_to=valid_to)
            coupon.save()
            messages.success(request,'Coupon added succesfully')
            return redirect('coupon')
        # if coupon_code!=coupon.coupon_code:
        #     coupon=Coupons.objects.create(coupon_code=coupon_code,description=description,minimum_amount=minimum_amount,discount=discount,valid_from=valid_from,valid_to=valid_to)
        #     coupon.save()
        #     return redirect('coupon')
        # else:
        #     messages.error(request,'Coupon Code already exist')
        #     return redirect('add-coupon')

    return render(request,'admin/add-coupon.html')


def edit_coupon(request,id):
    coupon=Coupons.objects.get(pk=id)
    if request.method=='POST':
        description=request.POST.get('description')
        minimum=request.POST.get('minimum_amount')
        discount=request.POST.get('discount')
        coupon.description=description
        coupon.minimum_amount=minimum
        coupon.discount=discount
        coupon.save()
        messages.info(request,'Coupon edited')
        return redirect('coupon')
    context={
        'coupon':coupon
    }
    return render(request,'admin/edit-coupon.html',context)

def delete_coupon(request,id):
    coupon=Coupons.objects.get(pk=id)
    coupon.delete()
    messages.info(request,'Coupon deleted')
    return redirect('coupon')


def offers(request):
    offers=CategoryOffer.objects.all()
    context={
        'offers':offers
    }
    return render(request,'admin/offers.html',context)


def add_offer(request):
    categories=Category.objects.all()
    if request.method=='POST':
        offer_name=request.POST.get('offer_name')
        category=request.POST.get('category')
        discount_percentage=request.POST.get('discount_percentage')
        expires_on=request.POST.get('valid_to')
        try:
            cat=Category.objects.get(id=category)
        except Category.DoesNotExist:
            messages.error(request,'Invalid category selected')
            return redirect('add-offer')
        if  CategoryOffer.objects.filter(Q(offer_name=offer_name) &Q(category=category)):
            messages.warning(request,'Offer already exist')
        else:
            offer=CategoryOffer.objects.create(offer_name=offer_name,valid_to=expires_on,category=cat,discount_percentage=discount_percentage)
            messages.info(request,'Offer added')
            return redirect('offer')
    context={
        'categories':categories
    }
    return render(request,'admin/add-offer.html',context)


def delete_offer(request,id):
    offer=CategoryOffer.objects.get(pk=id)
    offer.delete()
    messages.info(request,'Offer deleted')
    return redirect ('offer')