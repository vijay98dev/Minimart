from django.db import models
from django.urls import reverse
from django.utils import timezone
import datetime
from datetime import date




# Create your models here.
class Category(models.Model):
    category_name=models.CharField(max_length=50,unique=True)
    slug=models.SlugField(max_length=50,unique=True)
    description=models.TextField(max_length=255,blank=True)
    is_available=models.BooleanField(default=True)

    class Meta:
        verbose_name = ("Category")
        verbose_name_plural = ("Categories")

    def __str__(self):
        return self.category_name

    def get_url(self):
        return reverse("product_by_slug", args=[self.slug])
    
    def block(self):
        self.is_available=False
        self.save()

    def unblock(self):
        self.is_available=True
        self.save()

class CategoryOffer(models.Model):
    offer_name = models.CharField(max_length=100)
    valid_to = models.DateField()
    category = models.ForeignKey("category.Category", on_delete=models.CASCADE)
    discount_percentage = models.IntegerField()
    product = models.ForeignKey("store.Product", on_delete=models.CASCADE)   
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.offer_name

    def is_valid(self):
        now = timezone.now()
        if self.valid_to != now:
            self.is_active = True
            return self.is_active
        else:
            return self.is_active

    # def offer_amount(self):
    #     percentage=self.discount_percentage
    #     product_price=self.product.price
    #     offer_price=product_price-((product_price*percentage)/100)
    #     return offer_price  


