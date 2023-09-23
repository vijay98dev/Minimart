from django.db import models
from account.models import CustomUser
from store.models import Product,ProductImage,ProductSize
from django.utils import timezone
from datetime import date

# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True)
    user=models.ForeignKey("account.Customuser", on_delete=models.CASCADE)
    date_created=models.DateTimeField(auto_now_add=True)
    coupon=models.ForeignKey("cart.Coupons", on_delete=models.SET_NULL,null= True, blank=True)

    def __str__(self):
        return f'Cart for {self.user.username}'
    



class CartItems(models.Model):
    cart=models.ForeignKey("cart.Cart",on_delete=models.CASCADE)
    product=models.ForeignKey("store.ProductSize",on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=0)
    date_created=models.DateTimeField(auto_now_add=True)


    def __str__(self) -> str:
        return f'{self.product.product.product_name} -{self.quantity}'
    

    def sub_total(self):
        return self.product.price * self.quantity
    
    def tax(self):
        return (self.sub_total()*5)/100
    
    def total(self):
        return self.sub_total()+self.tax()
    
    def discount_amount(self):
        if self.cart.coupon is not None:
            discount=self.cart.coupon.discount
            return discount
        else:
            discount=0
            return discount
        
    def total_after_discount(self):
        total=self.total()
        discount=self.discount_amount()
        if discount is not None:
            return total-discount
        else:
            return total
        
class Wishlist(models.Model):
    user=models.ForeignKey("account.CustomUser",  on_delete=models.CASCADE)
    product=models.ForeignKey("store.Product", on_delete=models.CASCADE)



class Coupons(models.Model):
    coupon_code=models.CharField(max_length=100,unique=True)
    description=models.TextField()
    minimum_amount=models.IntegerField(default=2000)
    discount=models.IntegerField(default=0)
    is_expired=models.BooleanField(default=False)
    valid_from=models.DateTimeField()
    valid_to=models.DateTimeField()

    def __str__(self):
        return self.coupon_code
    

    def is_valid(self):
        now=timezone.now()
        if self.valid_to!=now:
            self.is_expired=True
            return self.is_expired
        else:
            return self.is_expired


class UserCoupons(models.Model):
    user=models.ForeignKey("account.CustomUser", on_delete=models.CASCADE)
    coupon=models.ForeignKey("cart.Coupons", on_delete=models.CASCADE)
    is_used=models.BooleanField(default=True)

