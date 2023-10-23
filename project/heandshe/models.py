from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from datetime import date



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")
         
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(unique=True)
    first_name  = models.CharField(max_length=30, blank=True)
    last_name   = models.CharField(max_length=30, blank=True)
    name        = models.CharField(max_length=30, blank=True)
    is_active   = models.BooleanField(default=True)
    is_staff    = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    phone_number=models.CharField(max_length=15,blank=True)
    wallet_bal= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    objects = CustomUserManager()
    
    groups = models.ManyToManyField(
        'auth.Group',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        blank=True,
        related_name='custom_users',
        related_query_name='custom_user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Category(models.Model):
    category_name=models.CharField(max_length=100)

    def __str__(self):
        return self.category_name


class Sub_category(models.Model):
    main_category=models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category_name=models.CharField(max_length=100)


    def __str__(self):
        return self.sub_category_name


class Section(models.Model):
    name=models.CharField(max_length=200)

    def __str__(self):
        return self.name



class Product(models.Model):
    product_name    = models.CharField(max_length=100)
    description     = models.CharField(max_length=1000, default='')
    category        = models.ForeignKey(Category,on_delete=models.CASCADE , blank=True , null=True)
    Sub_category    = models.ForeignKey(Sub_category,on_delete=models.CASCADE , null=True , blank=True)
    stock           = models.IntegerField(default=0)
    price           = models.IntegerField(default=0)
    image           = models.ImageField(upload_to='products/' , blank=True , null= True)
    section         =models.ForeignKey(Section,on_delete=models.CASCADE,blank=True,null=True)
    color          =models.CharField(max_length=100,null=True,blank=True)


    def __iter__(self):
        yield self.id
     
class Images(models.Model):
    product     =  models.ForeignKey(Product, on_delete=models.CASCADE)
    images      =  models.ImageField(upload_to='products/')


class Address(models.Model):
    user      =models.ForeignKey(CustomUser,on_delete=models.CASCADE,null = True,blank=True)
    full_name =models.CharField(max_length=100)
    house_no  =models.CharField(max_length=100)
    post_code =models.CharField(max_length=20)
    state     =models.CharField(max_length=50)
    street    =models.CharField(max_length=100)
    phone_no  =models.CharField(max_length=15,blank=True)
    city      =models.CharField(max_length=100)
    is_default=models.BooleanField(default=False)



class Wishlist(models.Model):
    user          =     models.ForeignKey(CustomUser,on_delete=models.CASCADE,null = True,blank=True)
    product       =     models.ForeignKey(Product,on_delete=models.CASCADE)
    image         =     models.ImageField(upload_to='products',null = True,blank=True)
    


    def __str__(self):
        return f"Wishlist:{self.user.name}-{self.product}"

    
# class ProductVariation(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     color   = models.CharField(max_length=50)
#     Brand   =models.CharField(max_length=100,null=True,blank=True)
#     price   = models.DecimalField(max_digits=10, decimal_places=2)
#     image   =models.ForeignKey(Images,on_delete=models.CASCADE,null=True,blank=True)
#     stock  =models.IntegerField(default=0)

#     def __str__(self):
#         return f"{self.product.product_name} - {self.size} - {self.color}"

class Cart(models.Model):
    user           =     models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    product        =     models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity       =     models.IntegerField(default=0)
    image          =     models.ImageField(upload_to='products',null=True, blank=True )

    
    @property
    def sub_total(self):
        return self.product.price * self.quantity

    def __str__(self):
          return f"Cart: {self.user.name} - {self.product} - Quantity: {self.quantity}"
    


class Order(models.Model):

    ORDER_STATUS = (
        ('pending', 'Pending'),
        ('processing','processing'),
        ('shipped','shipped'),
        ('delivered','delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('returned','returned'),
        ('refunded','refunded'),
        ('on_hold','on_hold')

    )

    user           =   models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    address        =   models.ForeignKey(Address, on_delete=models.CASCADE)
    product        =   models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    amount         =   models.CharField(max_length=100)  
    payment_type   =   models.CharField(max_length=100)  
    status         =   models.CharField(max_length=100, choices=ORDER_STATUS, default='pending' )  
    quantity       =   models.IntegerField(default=0, null=True, blank=True)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)
    date           =   models.DateField(default=date.today)
    
    def _str_(self):
        return f"Order #{self.pk} - {self.product}"

class OrderItem(models.Model):
    order          =   models.ForeignKey(Order,on_delete=models.CASCADE, null=True, blank=True)
    product        = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity       =   models.IntegerField(default=1)
    image          =   models.ImageField(upload_to='products', null=True, blank=True)

    def _str_(self):
        return str(self.id)
    


class Coupon(models.Model):
    coupon_code     =  models.CharField(max_length=100,null=True,blank=True)
    expired         =  models.BooleanField(default=False)
    discount_price  =  models.PositiveIntegerField(default=100)
    minimum_amount  =  models.PositiveIntegerField(default=500)
    expiry_date     =  models.DateField(null=True,blank=True)

    def __str__(self):
        return self.coupon_code

class Wallet(models.Model):
    user  =models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_credit = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status=models.CharField(max_length=20,blank=True)

    def _str_(self):
        return f"{self.amount} {self.is_credit}"

    def _iter_(self):
        yield self.pk





