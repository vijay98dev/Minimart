from django.db import models
from account.models import CustomUser,UserProfile
from django.utils.text import slugify
from store.models import ProductSize,ProductImage



# Create your models here.
class Payment(models.Model):
    PAYMENT_STATUS = (
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
 
    user=models.ForeignKey("account.CustomUser", on_delete=models.CASCADE)
    payment_method=models.CharField( max_length=100)
    amount_paid=models.CharField( max_length=100,default=0)
    status=models.CharField( max_length=100,choices=PAYMENT_STATUS,default='Pending')
    created_at=models.DateTimeField(  auto_now_add=True)
    razor_pay_order_id=models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_id=models.CharField(max_length=150, null=True, blank=True)
    razor_pay_payment_signature=models.CharField(max_length=150, null=True, blank=True)
    order=models.ForeignKey("orders.Order",on_delete=models.CASCADE)

    def __str__(self):
        return self.status
    

class Order(models.Model):
    ORDER_STATUS = (
    ('Processing','Processing'),
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Cancelled', 'Cancelled'),
    ('Out for Delivery', 'Out for Delivery'),
    ('Delivered', 'Delivered'),
   )
    

    user=models.ForeignKey("account.CustomUser",  on_delete=models.SET_NULL,null=True)
    order_number=models.CharField( max_length=50)
    address=models.ForeignKey("account.UserProfile",  on_delete=models.DO_NOTHING)
    order_total=models.DecimalField( max_digits=10, decimal_places=2)
    status=models.CharField( max_length=50,choices=ORDER_STATUS,default='Processing')
    created_at=models.DateTimeField( auto_now_add=True)
    slug  = models.CharField(max_length=200,null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    total=models.DecimalField( max_digits=10, decimal_places=2,default=0)
    tax=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount_price=models.DecimalField(max_digits=10, decimal_places=2,default=0)


    def __str__(self):
        return f"Order {self.pk} "
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.user.id) +str(self.order_number))
        return super().save(*args, **kwargs)


class OrderProduct(models.Model):
    order=models.ForeignKey("orders.Order",  on_delete=models.CASCADE)
    payment=models.ForeignKey("orders.Payment", on_delete=models.SET_NULL,null=True)
    user=models.ForeignKey("account.CustomUser",  on_delete=models.CASCADE)
    product=models.ForeignKey("store.ProductSize",  on_delete=models.CASCADE)
    product_image=models.ForeignKey("store.ProductImage",  on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=0)
    product_price=models.DecimalField(max_digits=10, decimal_places=2)
    sub_total=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    tax=models.DecimalField(max_digits=10, decimal_places=2,default=0)
    discount=models.DecimalField( max_digits=10, decimal_places=2,default=0)
    total=models.DecimalField( max_digits=10, decimal_places=2,default=0)
    created_at=models.DateTimeField( auto_now_add=True) 
    updated_at=models.DateTimeField(auto_now=True )


   
    def __str__(self):
        return f"{self.product.product.product_name} - {self.quantity}" 