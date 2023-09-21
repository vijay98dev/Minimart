from django.contrib import admin
from store.models import Product,ProductImage,ProductSize

# Register your models here.

class ProductSizeAdmin(admin.ModelAdmin):
    prepopulated_fields={'slug':('product__product_name'+'product_size',)}
    list_display=('product_size','slug','price','stock')

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(ProductSize)
