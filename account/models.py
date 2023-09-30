from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import uuid
# Create your models here.



class CustomUserManager(BaseUserManager):
    def create_user(self,first_name,last_name,phone_number,username,email,password=None):
        if not email:
            raise ValueError('Email address is manadatory')
        if not username:
            raise ValueError('Username address is manadatory')
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self,first_name,last_name,username,email,password):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_admin=True
        user.is_staff=True
        user.is_active=True
        user.is_superuser=True
        user.save(using=self._db)
        return user
class CustomUser(AbstractBaseUser):
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    username=models.CharField(max_length=50,unique=True)
    email=models.EmailField(max_length=50,unique=True)
    phone_number=models.CharField(max_length=50,blank=False,unique=True)
    otp=models.CharField(max_length=50,null=True,blank=True)
    uid=models.UUIDField(default=uuid.uuid4)


    date_joined=models.DateTimeField(auto_now_add=True)
    last_joined=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_staff=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_superuser=models.BooleanField(default=False)


    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','first_name','last_name']

    objects=CustomUserManager()

    def __str__(self) -> str:
        return self.email
    
    def has_perm(self, prem, obj=None):
        return self.is_admin
    
    def has_module_perms(self, add_label):
        return True
    


class UserProfile(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    address=models.CharField( max_length=250)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField( max_length=100)
    country = models.CharField( max_length=100)
    pin_code = models.CharField(max_length=10)
    profile_image=models.ImageField(upload_to='photo/profile-image', max_length=None,null=True,default='admin/assets/img/avatars/5.png')
    

    def __str__(self):
        return self.user.username