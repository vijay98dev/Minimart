from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from account.models import CustomUser

# Register your models here.

class CustomUserAdmin(UserAdmin):
    list_display=('email','first_name','last_name','username','last_joined','is_active')
    list_display_links=('email','first_name','last_name')
    readonly_fields=('last_joined','date_joined')

    filter_horizontal=()
    list_filter=()
    fieldsets=()

admin.site.register(CustomUser,CustomUserAdmin)