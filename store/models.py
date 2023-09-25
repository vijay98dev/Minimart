from collections.abc import Iterable
from django.db import models
from category.models import Category
from django.urls import reverse
from django.utils.text import slugify
from django.utils import timezone
import datetime
from datetime import date
# Create your models here.
class Product(models.Model):
    product_name=models.CharField(max_length=50,unique=True)        
    description=models.TextField(max_length=400,blank=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    is_available=models.BooleanField(default=True)
    offer_applied=models.BooleanField(default=False)
    slug=models.SlugField(max_length=100,unique=True)
    def __str__(self) -> str:
        return self.product_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.product_name}")
        return super().save(*args, **kwargs)

class ProductSize(models.Model):
    product_size=models.FloatField(max_length=5,blank=False)
    price=models.IntegerField()
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    is_delete=models.BooleanField(default=False)
    created_date=models.DateTimeField( auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    offer_price=models.IntegerField(default=0,null=True,blank=True)

    def __str__(self) -> str:
        return f'{self.product.product_name}'

    def soft_delete(self):
        self.is_delete=True
        self.save()

    

    def get_id(self):
        return reverse("edit-variant",args=[self.product.id,self.id])

class ProductImage(models.Model):
    product_image=models.ImageField(upload_to='photos/products', height_field=None, width_field=None, max_length=None)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size=models.ForeignKey(ProductSize, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.product_image
    
    def get_url(self):
        return reverse("product_details", args=[self.product.category.slug,self.product.slug])
    


