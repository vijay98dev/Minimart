from django.shortcuts import get_object_or_404, render,redirect
from django.urls import reverse
from account.forms import RegistrationForm
from account.models import CustomUser,UserProfile
from account.helper import MessageHandler
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
import random
from orders.models import Order,OrderProduct


# Create your views here.
def register(request):
    if request.method=='POST':
        form=RegistrationForm(request.POST)
        users=CustomUser.objects.all()
        if form.is_valid():
            first_name=form.cleaned_data['first_name']
            last_name=form.cleaned_data['last_name']
            email=form.cleaned_data['email']
            phone_number=form.cleaned_data['phone_number']
            password=form.cleaned_data['password']
            username=email.split("@")[0]
            # if email == user.email:
            #     messages.info(request,'Email already taken')
            #     return redirect('register')
            # elif phone_number == user.phone_number:
            #     messages.info(request,'Phone number already exists')
            #     return redirect('register')
            # else:
            user=CustomUser.objects.create_user(first_name=first_name,last_name=last_name,email=email,username=username,password=password,phone_number=phone_number)
            messages.success(request,'Registration Sucessful')
            return redirect('signin')
    else:
        form=RegistrationForm()
    context={
        'form':form
    }
    return render(request,'user/register.html',context)

def signin(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        user=authenticate(email=email,password=password)
        if user is not None:
            login(request,user)
            return redirect('index')
        else:
            messages.info(request,'Invalid Credentails')
            return redirect('signin')
    return render(request,'user/signin.html')

def verify_number(request):
    user=None
    if request.method=='POST':
        phone_number=request.POST.get('phone_number')
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            user=CustomUser.objects.get(phone_number__exact=phone_number)
            user.otp=random.randint(1000,9999)
            user.save()
            message_handler=MessageHandler(phone_number,user.otp).send_otp_on_phone()
            messages.success(request,'Otp number for verification has been sent')
            return redirect(reverse('confirm_otp', args=[user.id]))
        else:
            messages.error(request,'Phone number is not in the database.Please enter a valid number')

    return render(request,'user/verify_number.html',{'user':user})

def confirm_otp(request,id):
    user=CustomUser.objects.get(id=id)
    if request.method=='POST':
        otp=request.POST.get('otp-verify')
        if otp == user.otp:
            return redirect (reverse('change_password', args=[user.id]))

    return render(request,'user/confirm_otp.html',{'user':user})

def change_password(request,id):
    user=CustomUser.objects.get(id=id)
    if request.method=='POST':
        new_password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        if new_password==confirm_password:
            user.set_password(new_password)
            user.save()
            password=user.password
            return redirect('signin')
        else:
            messages.error(request,"Password doesn't match")
            return redirect(reverse('change_password',args=[user.id]))
    return render(request,'user/change_password.html',{'user':user})
@login_required(login_url='signin')
def signout(request):
    logout(request)
    messages.success(request,"Logout was successful.")
    return redirect('signin')


def profile(request):
    user=request.user
    profile=UserProfile.objects.filter(user=user)
    if profile.exists():
        profile=profile.all()
    else:
        profile=None
    order=Order.objects.filter(user=user).count()

    context={
        'users':user,
        'profile':profile,
        'order':order
    }
    return render(request,'user/profile.html',context)

def add_address(request):
    user=request.user
    if request.method=='POST':
        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        address=request.POST.get('address')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        country=request.POST.get('country')
        pin_code=request.POST.get('pin_code')
        if len(pin_code)==6:
            profile=UserProfile(user=user)
            profile.first_name=first_name
            profile.last_name=last_name
            profile.address=address
            profile.street=street
            profile.city=city
            profile.state=state
            profile.country=country
            profile.pin_code=pin_code
            profile.save()
            source = request.GET.get('source', 'checkout')
            if source == 'checkout':
                messages.success(request, 'Address saved successfully')
                return redirect('checkout')  # Redirect to the checkout page
            else:
                messages.success(request, 'Address saved successfully')
                return redirect('add-address')  # Redirect to the add address page
                
        else:
            messages.error(request,'Enter a valid address')
    return render(request,'user/add-address.html')

def address(request):
    user=request.user
    profile=UserProfile.objects.filter(user=user)
    context={
        'user':user,
        'profile':profile
    }
    return render(request,'user/address.html',context)


def edit_address(request,id) :
    user=request.user
    profile=UserProfile.objects.get(id=id)
    if request.method=='POST':
        address=request.POST.get('address')
        street=request.POST.get('street')
        city=request.POST.get('city')
        state=request.POST.get('state')
        country=request.POST.get('country')
        pin_code=request.POST.get('pin_code')

        profile.address=address
        profile.street=street
        profile.city=city
        profile.state=state
        profile.country=country
        profile.pin_code=pin_code
        profile.save()
        return redirect('address')
    messages.success(request,'Address changed successfull')
    context={
        'user':user,
        'profile':profile
    }
    return render(request,'user/edit-address.html',context)

def delete_address(request,id):
    user=request.user
    profile=UserProfile.objects.get(id=id,user=user)
    profile.delete()
    return redirect('address')

def reset_password(request):
    user=request.user
    if request.method=='POST':
        current=request.POST.get('current_password')
        new=request.POST.get('new_password')
        cofirm=request.POST.get('cofirm_password')
        if user.check_password(current):
            if new==cofirm:
                user.set_password(new)
                user.save()
                messages.success(request,'Password Reset Successful')
                return redirect('profile')
            else:
                messages.error(request,'Entered password does not match')
                return redirect('reset')
    return render(request,'user/reset-password.html')
        

def order_list(request):
    user=request.user
    order=Order.objects.filter(user=user)
    order_items=OrderProduct.objects.filter(order=order)
    contex={
        'order':order,
        'order_item':order_items,
    }
    return render(request,'user/order-list.html',contex)

def edit_profile(request):
    user=request.user
    profile=UserProfile.objects.filter(user=user)
    if profile.exists():
        profile=profile.all()
    else:
        profile=None
    if request.method=='POST':
        username=request.POST.get('username') 
        phone_number=request.POST.get('phone_number') 
        email=request.POST.get('email') 

        if username !=user.username and CustomUser.objects.filter(username=username).exists():
            messages.error(request,'Username not available')
        elif phone_number !=user.phone_number and CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request,'Provide another Phone number')
        elif email !=user.email and CustomUser.objects.filter(email=email).exists():
            messages.error(request,'Provide another Email')
        else:
            user.username=username
            user.phone_number=phone_number
            user.email=email
            user.save()
        messages.success(request,'Changes made Successful')
        return redirect('profile')
    context={
        'users':user,
        'profile':profile
    }
    return render(request,'user/edit-profile.html',context)