from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from .models import*
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from django.core.exceptions import ObjectDoesNotExist
import smtplib
import secrets
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User,auth
from django.contrib.auth import authenticate,login
from django.http import JsonResponse
import json
from django.db.models import Count
from decimal import Decimal
from django.http import FileResponse
from reportlab.lib.pagesizes import letter,inch
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
import base64
import matplotlib.pyplot as plt
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from reportlab.lib.pagesizes import A4
from django.template.loader import render_to_string
from xhtml2pdf import pisa 
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from django.contrib import messages
from django.core.mail import send_mail
from email.mime.text import MIMEText
import traceback
import io
import re
from django.db.models import Q
# Create your views here.

def base(request):
    return render(request,'base.html')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def home(request):
    if 'admin' in request.session:
        return redirect('dashboard')
    section = Section.objects.filter(id=1).first()
    product = Product.objects.filter(section_id=1)
    banner = Banner.objects.all()
    search_query = request.GET.get('q')
    if search_query:
        # If there is a search query, perform the search
        products = Product.objects.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    else:
        # If no search query, return all products in the specified section
        products = product
    context = {
        'section': section,
        'products': products,
        'banner': banner,
        'search_query': search_query,
    }
    return render(request, 'home.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def adminlogin(request):
    if 'admin' in request.session:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            email      =  request.POST.get('email')
            password        =  request.POST.get('password')
            user          =  authenticate(request,email=email,password = password)
            if user is not None and user.is_superuser:
                login(request,user)
                request.session['admin']=email
                return redirect('dashboard')
            else:
                messages.error(request,"email or password is not same")
                return render(request, 'adminlogin.html') 
        else:
             return render (request,'adminlogin.html')


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def dashboard(request):
    if 'admin' in request.session:
        products = Product.objects.order_by('-id')
        # Process product data for bar chart (order distribution)
        order_labels = [f'Order {product.id}' for product in products]
        order_amounts = [product.price for product in products]  # Use any field you want for the order amount
        # Process product data for pie chart (stock distribution)
        stock_labels = [product.product_name for product in products]
        stock_amounts = [product.stock for product in products]
        # Convert data to JSON format for JavaScript
        order_data = json.dumps(order_amounts)
        stock_data = json.dumps(stock_amounts)
        context = {
            'order_labels': order_labels,
            'order_data': order_data,
            'stock_labels': stock_labels,
            'stock_data': stock_data,
        }
        return render(request, 'dashboard.html', context)
    else:
        return redirect('admin')
  
    
@never_cache   
def admin_logout(request):
    if 'admin' in request.session:
        request.session.flush()
    logout(request)
    return redirect('adminlogin')

@never_cache 
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def customers(request):
    if 'admin' in request.session:    
        customer_list =  CustomUser.objects.filter(is_staff=False).order_by('id')
        paginator = Paginator(customer_list,10)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,
        }
        return render(request, 'customer.html', context)
    else:
        return redirect('adminlogin')
    

def unblock_customer(request, customer_id):
    try:
        customer = CustomUser.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return redirect('customer')  
    # toggles is set if is active is false it will be set to true and vice versa 
    customer.is_active = not customer.is_active    
    customer.save()
    return redirect('customer')


def block_customer(request, customer_id):
    try:
        customer = CustomUser.objects.get(id=customer_id)
    except CustomUser.DoesNotExist:
        return redirect('customer')  
    customer.is_active = False
    customer.save()
    return redirect('customer')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def signup(request):
    if 'email'in request.session:
        return redirect('home') 
    elif request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone_number=request.POST['phone_number']
        password=request.POST['password']
        confirmpassword=request.POST['confirmpassword']
        user=authenticate(email=email,password=password)
        if not (name and email and password and phone_number and confirmpassword):
            messages.info(request,"PLease Fill Required field")
            return redirect('signup')
        elif password != confirmpassword:
            messages.info(request,"PAssword Missmatch")
            return redirect('signup')
        elif not is_valid_password(password):
            messages.error(request,"password should contain atleast one capital,one special character,one number and have least of 8 characters")
            return redirect('signup')
        elif not validate_email(email):
            messages.error(request, "Please enter a valid email address")
            return redirect('signup')
        elif not validate_number(phone_number):
            messages.error(request, "Please enter a valid mobile number")
            return redirect('signup')
        else:
            if CustomUser.objects.filter(email = email).exists():
                messages.info(request,"Email Already Taken")
                return redirect('signup')
            elif CustomUser.objects.filter(phone_number = phone_number).exists():
                messages.info(request,"phone number already taken")
                return redirect('signup')
            else:
                my_user=CustomUser.objects.create_user(name=name,email=email,password=password,phone_number=phone_number)
                my_user.save()
        message = generate_otp()
        sender_email = "heandshe2206@gmail.com"
        receiver_mail = email
        password_email = "nyxbksyvujbbkmdh"
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, password_email)
                server.sendmail(sender_email, receiver_mail, message)
        except smtplib.SMTPAuthenticationError:
            messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
            return redirect('login')
        request.session['email'] =  email
        request.session['otp']   =  message
        messages.success (request, 'OTP is sent to your email')
        print("..............reac")
        return redirect('verify_signup')
    return render(request,'signup.html')

  
def validate_email(email):
    return "@" in email and "." in email


def validate_number(number):
    pattern = r"^\d{10}$"
    if re.match(pattern, number):
        return True
    else:
        return False

def is_valid_password(password):
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@#$%^&+=!]).{8,}$"
    if re.match(pattern, password):
        return True
    else:
        return False
  
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def verify_signup(request):
    context = {
        'messages': messages.get_messages(request)
    }
    if request.method == "POST":
        user      = CustomUser.objects.get(email=request.session['email'])
        x         =  request.session.get('otp')
        OTP       =  request.POST['otp']
        if OTP == x:
            user.is_verified = True
            user.save()
            del request.session['email'] 
            del request.session['otp']
            login(request,user)
            messages.success(request, "Signup successfull!")
            return redirect('login')
        else:
            user.delete()
            messages.info(request,"invalid otp")
            del request.session['email']
            return redirect('signup')
    return render(request,'verify_signup.html',context)
       

    
# Send the OTP via email
def generate_otp(length = 6):
    return ''.join(secrets.choice("0123456789") for i in range(length)) 
    
@never_cache
def user_login(request):
    if 'email' and 'otp' in request.session:
        request.session.flush()
        return redirect('login')
    if 'email' in request.session:
        return redirect('home')
    if 'admin' in request.session:
        return redirect('admin')
    if request.method == "POST":
        email = request.POST.get('email')  
        password = request.POST.get('password')
        # Authenticate against your custom Customer model using email
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            request.session['email']=email
            return redirect('home')
        else:
            messages.error(request, 'Email and password are invalid!')
            return redirect('login')
    return render(request, 'login.html')


@never_cache
def logout(request):
    if 'email' in request.session:
        request.session.flush()
        logout(request)
    return redirect('login')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def category(request):
    if 'admin' in request.session:
        categories = Category.objects.all().order_by('id')
        paginator = Paginator(categories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'categories': page_obj,
        }
        return render(request, 'category.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def add_category(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            category_name       =   request.POST.get('category_name')
            category_offer_description=request.POST.get('category_offer_description')
            category_offer=request.POST.get('category_offer')
            category = Category.objects.create(category_name = category_name,category_offer_description=category_offer_description,category_offer=category_offer)   
            category.save() 
            return redirect('category')  
        return render(request, 'add_category.html') 
    else:
        return redirect ('admin')

    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_category(request, id):
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return HttpResponse("Error")
    if request.method == 'POST':
        category_name               = request.POST.get('category_name')
        category_offer_description  =request.POST.get('category_offer_description')
        category_offer  =request.POST.get('category_offer')
        if category_name:
            category.category_name               =  category_name
            category.category_offer_description  =category_offer_description
            category.category_offer              =category_offer
        category.save()
        return redirect('category')
    context = {'category': category}
    return render(request, 'edit_category.html', context)
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_category(request, category_id):
    if 'admin' in request.session:
        try:
            category = Category.objects.get(id=category_id)
        except Category.DoesNotExist:
            return render(request, 'category_not_found.html')
        context = {'category': category}
        return render(request, 'edit_category.html', context)
    else:
        return redirect ('admin')

def delete_category(request, category_id):
    try:
         category = Category.objects.get(id=category_id)
         category.active = True
         category.save()
    except Category.DoesNotExist:
         return HttpResponse("Category Not Found")
    category = Category.objects.all()
    context={'category':category}
    return redirect('category')

def restore_category(request,category_id):
    try:
        category=Category.objects.get(id=category_id)
        category.active=False
        category.save()
    except Category.DoesNotExist:
        return HttpResponse("Category Not Found")
    return redirect('category')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def sub_category(request):
    if 'admin' in request.session:
        subcategories = Sub_category.objects.all()
        maincategories = Category.objects.all()
        maincategory_names = {}
        maincategory_ids = {}
        for sub in subcategories:
            maincategory_names[sub.id] = sub.main_category.category_name
            maincategory_ids[sub.id] = sub.main_category.id          
        paginator = Paginator(subcategories, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'categories': page_obj,
            'subcategories' : subcategories,
            'maincategories' :maincategories,
            'maincategory_names': maincategory_names,
            'maincategory_ids': maincategory_ids,
        }
        return render(request,'sub_category.html',context)
    else:
        return redirect('admin')


def add_sub_category(request):
    main_category=Category.objects.all()
    context={
        'main_category':main_category
    }
    if 'admin' in request.session: 
        if request.method  == 'POST':
            cat      = request.POST.get('categories')
            print(cat)
            sub_category_name   =request.POST.get('name')
            main = Category.objects.get(id=cat)
            sub = Sub_category.objects.create(main_category=main,sub_category_name=sub_category_name)
            sub.save() 
            return redirect('sub_category')  
        return render(request,'add_sub_category.html',context)
    else:
        return redirect ('admin')
       
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_sub_category(request, sub_category_id):
    cat = Category.objects.all()
    if 'admin' in request.session:
        try:
            sub_category =  Sub_category.objects.get(id=sub_category_id)
        except  Sub_category.DoesNotExist:
            return render(request, 'category_not_found.html')

        context = {'sub_category': sub_category,'cat':cat,
        }
        return render(request, 'edit_sub_category.html', context)
    else:
        return redirect ('admin')
    

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_sub_category(request, sub_category_id):
    main_category = Category.objects.all()
    sub_category = Sub_category.objects.get(id=sub_category_id)  # Use get() instead of filter()
    if request.method == 'POST':
        new_name = request.POST.get('sub_category_name')
        new_main_id = request.POST.get('main_category')
        sub_category.sub_category_name = new_name
        # sub_category.main_category_id = new_main_id
        sub_category.save()
        return redirect('sub_category')
    return render(request, 'edit_sub_category.html')

def delete_sub_category(request,sub_id):
    try:
        sub_category = Sub_category.objects.get(id=sub_id)
        sub_category.active = not sub_category.active
        sub_category.save()
        messages.success(request, 'Subcategory deactivated.')
    except Sub_category.DoesNotExist:
        messages.error(request, 'Subcategory not found.')
        return render(request, 'sub_category_not_found.html')
    return redirect('sub_category')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        products  = Product.objects.all().order_by('id')       
        paginator = Paginator(products, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'page_obj': page_obj,  
        }
        return render(request, 'product.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def add_product(request):
    categories = Category.objects.all()
    sections = Section.objects.all()
    if 'admin' in request.session:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            description = request.POST.get('description')
            subcategory_id = request.POST.get('subcategory_id')
            section_name = request.POST.get('section')  # Get the section name
            color=request.POST.get('color')
            stock = request.POST.get('stock')
            price = request.POST.get('price')
            offer=request.POST.get('offer')
            image = request.FILES.get('image')
            try:
                subcategory = Sub_category.objects.get(id=subcategory_id)
                main_category = subcategory.main_category
                # Fetch the Section instance based on the section name
                section = Section.objects.get(name=section_name)
                product = Product.objects.create(
                    product_name=product_name,
                    description=description,
                    Sub_category=subcategory,
                    category=main_category,
                    section=section,  # Assign the Section instance
                    color=color,
                    stock=stock,
                    product_offer=offer,
                    price=price,
                    image=image,
                )
                for image in request.FILES.getlist('image'):
                    Images.objects.create(product=product, images=image)
                return redirect('product')
            except (Sub_category.DoesNotExist, Section.DoesNotExist):
                return HttpResponse("Sub Category or Section not found")
        context = {'categories': categories, 'sections': sections,}
        return render(request, 'add_product.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_product(request, product_id):
    if 'admin' in request.session:
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return render(request, 'product_not_found.html')
        categories = Category.objects.all()
        sections=Section.objects.all()
        context = {
            'product'    : product,
            'categories' : categories,
            'sections'   :sections,
        }
        return render(request, 'edit_product.html', context)
    else:
        return redirect('admin')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_product(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.product_name = request.POST.get('product_name')
        product.description = request.POST.get('description')
        if request.POST.get('category'):
            category_name = request.POST.get('category')
            category = Category.objects.get(category_name=category_name)
            product.category = category
        # Fetch the Section instance based on the section name
        if request.POST.get('section'):
            section_name = request.POST.get('section')
            try:
                section = Section.objects.get(name=section_name)
                product.section = section
            except Section.DoesNotExist:
                # Handle the case where the section does not exist
                return HttpResponse("Section not found")
        product.color = request.POST.get('color')
        product.stock = request.POST.get('stock')
        product.product_offer = request.POST.get('offer')
        product.price = request.POST.get('price')
        image = request.FILES.get('image')
        if image:
            product.image = image
        product.save()
        mul_image=request.FILES.getlist('images')
        if mul_image:
            for image in mul_image:
                im = Images(product=product, images=image)
                im.save()
        return redirect('product')
    else:
        context = {
            'product': product,
        }
        return render(request, 'product.html', context)
    

def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.deleted = True
        product.save()
    except Product.DoesNotExist:
         return render(request, 'product_not_found.html')
    return redirect('product')

def restore_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        product.deleted = False  
        product.save()
    except Product.DoesNotExist:
        pass
    return redirect('product')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def userproductpage(request,id):
    product = Product.objects.filter(id=id).first()
    discounted_price = None
    offer_price = None
    if product.category.category_offer:
        discounted_price = (product.price - (product.price*product.category.category_offer/100))
    product.discounted_price = discounted_price
    if product.product_offer:
        offer_price        = product.price -(product.price * product.product_offer/100)
    product.offer_price    = offer_price
    context = {
        'product': product,
        'discounted_price': discounted_price, 
    }
    return render(request, 'product_details.html', context)

def shop(request):
    # Get all products and unique colors
    all_products = Product.objects.filter(deleted=False)
    unique_colors = Product.objects.values('color').annotate(count=Count('color')).order_by('color')
    brands = Product.objects.values_list('product_name', flat=True).distinct()
    # Filter products based on brand, color, and price
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_price = request.GET.get('price')
    selected_subcategory = request.GET.get('sub_category')
    # Start with all products and filter based on selected options
    products = all_products
    for product in products:
        discounted_price = None
        if product.category.category_offer:
            discounted_price = (product.price - (product.price*product.category.category_offer/100))
        product.discounted_price = discounted_price
        offer_price = None
        if product.product_offer:
            offer_price        =  product.price -(product.price * product.product_offer/100)
        product.offer_price    =  offer_price
    if selected_brand:
        products = products.filter(product_name=selected_brand)  # Use 'product_name' for brand filtering
    if selected_color:
        products = products.filter(color=selected_color)
    if selected_subcategory:
        # Filter for products with the selected subcategory
       products = products.filter(Sub_category__sub_category_name=selected_subcategory)
    if selected_price:
        # Define price ranges based on selected_price
        price_ranges = {
            "price1": (0, 500),
            "price2": (500, 1000),
            "price3": (1000, 5000),
            "price4": (5000, 10000),
            "price5": (10000, 25000),
            "price6": (25000, 50000),
            "price7": (50000, 1000000)  
        }
        if selected_price in price_ranges:
            price_range = price_ranges[selected_price]
            # Filter for products with prices within the selected price range
            products = products.filter(price__range=price_range)
    subcategories = Sub_category.objects.values('sub_category_name').distinct()
    context = {
        'all_products': all_products,
        'products': products,
        'unique_colors': unique_colors,
        'brands': brands,  
        'subcategories':  subcategories,
    }
    return render(request, 'shop.html', context)

@never_cache
def profile(request):
    if 'email' in request.session:
        user=request.user
        context={
            'user':user,
        }
        return render(request,'profile.html',context)
    return redirect('logout')


def update_profile(request):
    if request.method=='POST':
        user=request.user
    # retrive  data  from form
        new_name=request.POST['name']
        new_mail=request.POST['email']
        new_phone_number=request.POST['phone_number']
    # update the users info
        user.name=new_name
        user.email=new_mail
        user.phone_number=new_phone_number
        user.save()
        messages.success(request,'Profile updated successfully!!!')
        return redirect('profile')
    return render(request,'profile.html')


def address(request):
    # Assuming you have a foreign key from Address to the User model
    user = request.user
    addresses = Address.objects.filter(user=user)
    context={
        'addresses':addresses,
    }
    return render(request,'address.html',context)

def add_address(request):
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        # Create a new Address object and save it to the database
        user=request.user
        address = Address(
            user=user,
            full_name=full_name,
            house_no=house_no,
            post_code=post_code,
            state=state,
            street=street,
            phone_no=phone_no,
            city=city,
        )
        address.save()
        return redirect('address') # Redirect to the address list page or any other page
    return render(request,'add_address.html') 
    
def edit_address(request,id):
    address= Address.objects.get(id=id)
    if request.method == 'POST':
        # Retrieve data from the POST request
        full_name = request.POST['full_name']
        house_no = request.POST['house_no']
        post_code = request.POST['post_code']
        state = request.POST['state']
        street = request.POST['street']
        phone_no = request.POST['phone_no']
        city = request.POST['city']
        # Update the Address object with the edited data
        address.full_name = full_name
        address.house_no = house_no
        address.post_code = post_code
        address.state = state
        address.street = street
        address.phone_no = phone_no
        address.city = city
        # Save the updated address to the database
        address.save()
        return redirect('address')
    else:
        context = {
            'address': address
        }
    return render(request,'edit_address.html',context)


def delete_address(request,id):
    try:
        address = Address.objects.get(id=id)
    except Address.DoesNotExist:
        return render(request, 'Address_not_found.html')

    address.delete()
    return redirect('address')



def changepassword(request):
    if request.method == 'POST':
        old_password = request.POST.get('old')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        customer = CustomUser.objects.get(name=request.user.name)
        if customer.check_password(old_password):
            if new_password == confirm_password:
                customer.set_password(new_password)
                customer.save()
                # messages.success(request, 'Password changed successfully.')
                return redirect('home')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect ('profile')
        else:
            messages.error(request, 'Old password is incorrect.')
            return redirect('profile')

    return render(request, 'profile.html')

#wishlist
def wishlist(request):
    user = request.user
    wishlist_items = Wishlist.objects.filter(user=user)
    context = {
        'wishlist_items': wishlist_items
    }
    return render(request, 'wishlist.html', context)


def add_to_wishlist(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('product_not_found')
    user = request.user
    # Unpack the tuple returned by get_or_create
    wishlist, created = Wishlist.objects.get_or_create(product=product, user=user)
    # Check if the object was created or retrieved
    if created:
        # If it was created, you might want to do something specific
        pass
    # Call save() on the Wishlist object, not on the tuple
    wishlist.save()
    return redirect('wishlist')


def remove_from_wishlist(request, wishlist_item_id):
    try:
        if request.user.is_authenticated:
            wishlist_item = Wishlist.objects.get(id=wishlist_item_id, user=request.user)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
        pass
    return redirect('wishlist')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cartt(request):
    if 'discount' in request.session:
        del request.session['discount']
    user = request.user
    cart_items = Cart.objects.filter(user=user).order_by('id')
    subtotal = 0
    total_dict = {}

 

    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
            item_price = Decimal(0)
        elif cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.category.category_offer / 100)) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price
        elif cart_item.product.product_offer:
            item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer / 100)) * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price
        else:
            item_price = cart_item.product.price * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

    shipping_cost = 10
    total = subtotal + shipping_cost
    coupons = Coupon.objects.all()

    # Checking if the user has already used the coupon
    if 'discount' in request.session:
        discount = float(request.session['discount'])
        total -= discount

            # Mark the coupon a
    for cart_item in cart_items:
        cart_item.total_price = total_dict.get(cart_item.id, 0)
        cart_item.save()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'coupons': coupons,
    }
    return render(request, 'cartt.html', context)

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request,id):
    try:
        product = Product.objects.get(id=id)
    except Product.DoesNotExist:
        return redirect('product_not_found')
    quantity = request.POST.get('quantity', 1)
    if not quantity:
        quantity = 1
    else:
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
        if created:
            cart_item.quantity = int(quantity)
        else:
            cart_item.quantity += int(quantity)
        cart_item.save()
    return redirect('cartt')

def update_cart(request, productId):
    cart_item = None
    cart_item = get_object_or_404(Cart, product_id=productId, user=request.user)
    try:
        data = json.loads(request.body)
        quantity = int(data.get('quantity'))
    except (json.JSONDecodeError, ValueError, TypeError):
        return JsonResponse({'message': 'Invalid quantity.'}, status=400)
    if quantity < 1:
        return JsonResponse({'message': 'Quantity must be at least 1.'}, status=400)
    cart_item.quantity = quantity
    cart_item.save()
    return JsonResponse({'message': 'Cart item updated.'}, status=200)

@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def remove_from_cart(request,id):
    try:
        cart_item = Cart.objects.get(id=id, user=request.user)
        cart_item.delete()
    except Cart.DoesNotExist:
        pass
    return redirect('cartt')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def check_out(request):  
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal = 0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    discount = request.session.get('discount',0)
    if discount:
        total = subtotal + shipping_cost - discount if subtotal else 0
    else:
        total = subtotal + shipping_cost if subtotal else 0
    address = Address.objects.filter(user=user)
    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount_amount': discount,
        'total': total,
        'address': address,
    }
    return render(request, 'check_out.html', context)

def shipping_address(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        house_no = request.POST.get('house_no')
        post_code = request.POST.get('post_code')
        state = request.POST.get('state')
        street = request.POST.get('street')
        phone_no = request.POST.get('phone_no')
        city = request.POST.get('city')
        if not full_name or not house_no or not post_code or not state or not street or not phone_no or not city :
            messages.error(request, 'Please input all the details!!!')
            return redirect('check_out') 
        user = request.user
        address = Address.objects.create(
            user=user,
            full_name = full_name,
            house_no = house_no,
            post_code = post_code,
            state = state,
            street = street,
            phone_no = phone_no,
            city = city,
        )
        return redirect('check_out')
    else:
        return render(request, 'check_out.html')
    

def razor_pay(request,address_id):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    discount = request.session.get('discount', 0)
    if discount:
        total -= discount 
    payment  =  'razorpay'
    user     = request.user
    cart_items = Cart.objects.filter(user=user)
    address = Address.objects.get(id=address_id)
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )
    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    cart_items.delete()
    return redirect('success')

@login_required
def order_placed(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    discount = request.session.get('discount', 0)
    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        address_id    =    request.POST.get('addressId')
    if not address_id:
        messages.info(request, 'Input Address!!!')
        return redirect('check_out')
    if discount:
        coupon=get_object_or_404(Coupon,discount_price=discount)

        # user_coupon_usage, created = UsedCoupon.objects.get_or_create(
        # user=user,coupon=coupon)
        user_coupon = UsedCoupon.objects.create(user = user , coupon=coupon,is_used = True)
        total -= discount
    address = Address.objects.get(id=request.POST.get('addressId'))
    order = Order.objects.create(
        user          =     user,
        address       =     address,
        amount        =     total,
        payment_type  =     payment,
    )
    for cart_item in cart_items:
        product = cart_item.product
        product.stock -= cart_item.quantity
        product.save()
        order_item = OrderItem.objects.create(
            order         =     order,
            product       =     cart_item.product,
            quantity      =     cart_item.quantity,
            image         =     cart_item.product.image  
        )
    cart_items.delete()
    return redirect('success')


def success(request):
    orders = Order.objects.order_by('-id')[:1]
    context = {
        'orders'  : orders,
    }
    return render(request,'order_placed.html',context)


def restock_products(order):
    order_items = OrderItem.objects.filter(order=order)
    for order_item in order_items:
        product = order_item.product
        product.stock += order_item.quantity
        product.save()
    
# admin side order
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache     
def order(request):
    if 'admin' in request.session:
        orders = Order.objects.all().order_by('-id')
        paginator = Paginator(orders, per_page=10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'orders': page_obj,
        }
        return render(request, 'orders.html', context)
    else:
        return redirect('admin')

def updateorder(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('order') 
        # Check if the order status is already 'cancelled' and disallow changing it
        if order.status == 'cancelled':
            messages.error(request, 'Cancelled orders cannot have their status updated.')
            return redirect('order')

        order.status = new_status
        order.save()   
        messages.success(request, 'Order status updated successfully.')
        return redirect('order') 
    return redirect('admin')

# costumer side
def customer_order(request):
    user = request.user 
    orders = Order.objects.filter(user = user).order_by('-id')
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'customer_order.html',context)

def order_details(request,id):
    orders = Order.objects.filter(id=id)
    discount = request.session.get('discount',0)
    print(orders)
    context ={
         'orders':orders,
         'discount_amount': discount,
        }
    return render(request,'order_details.html',context)

def cancel_order(request, id):
    user=request.user
    usercustm=CustomUser.objects.get(email=user)
    order = Order.objects.get(id=id)
    if  order.status == 'completed' and  order.payment_type=='cod':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    elif  order.payment_type=='razorpay':
        wallet= Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='cancelled'
        order.save()
        Order_item_amount = Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        print('wallte:',usercustm.wallet_bal)
        usercustm.save()
    restock_products(order)
    order.status = 'cancelled'
    order.save()
    return redirect('order_details',id)

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            customer = CustomUser.objects.get(email=email) 
            if customer.email == email:
                message = generate_otp()
                sender_email = "heandshe2206@gmail.com"
                receiver_mail = email
                password_email = "nyxbksyvujbbkmdh"
                try:
                    with smtplib.SMTP("smtp.gmail.com", 587) as server:
                        server.starttls()
                        server.login(sender_email, password_email)
                        server.sendmail(sender_email, receiver_mail, message)
                except smtplib.SMTPAuthenticationError:
                    messages.error(request, 'Failed to send OTP email. Please check your email configuration.')
                    return redirect('signup') 
                request.session['email'] =  email
                request.session['otp']   =  message
                messages.success (request, 'OTP is sent to your email')
                return redirect('reset_password')         
        except CustomUser.DoesNotExist:
            messages.info(request,"Email is not valid")
            return redirect('login')
    else:
        return redirect('login')


def reset_password(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        stored_otp = request.session.get('otp')
        if entered_otp == stored_otp:
            if new_password == confirm_password:
                email = request.session.get('email')
                try:
                    customer = CustomUser.objects.get(email=email)
                    customer.set_password(new_password)
                    customer.save()
                    del request.session['email'] 
                    del request.session['otp']
                    messages.success(request, 'Password reset successful. Please login with your new password.')
                    return redirect('login')
                except CustomUser.DoesNotExist:
                    messages.error(request, 'Failed to reset password. Please try again later.')
                    return redirect('login')
            else:
                messages.error(request, 'New password and confirm password do not match.')
                return redirect('reset_password')
        else:
            messages.error(request, 'Invalid OTP. Please enter the correct OTP.')
            return redirect('reset_password')
    else:
        return render(request, 'forgot_pass.html')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def section(request):
    if 'admin' in request.session:
        sections = Section.objects.all().order_by('id')
        paginator = Paginator(sections, per_page=3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {
            'sections': page_obj,
        }
        return render(request, 'section.html', context)
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache          
def add_section(request):
    if 'admin' in request.session:
        if request.method  == 'POST':
            name   =   request.POST['name']
            section = Section.objects.create(
             name  =  name,           
            )
            section.save() 
            return redirect('section')  
        return render(request, 'add_section.html') 
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_section(request, section_id):
    if 'admin' in request.session:
        try:
            section = Section.objects.get(id=section_id)
        except Section.DoesNotExist:
            return HttpResponse("section doesnot exist")
        context = {'section': section}
        return render(request, 'edit_section.html', context)
    else:
        return redirect ('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_section(request, id):
    try:
        section = Section.objects.get(id=id)
    except Section.DoesNotExist:
        return render(request, 'category_not_found.html')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            section.name = name
        section.save()
        return redirect('section')
    context = {'section': section}
    return render(request, 'edit_section.html', context)

def delete_section(request,section_id):
    try:
        section = Section.objects.get(id=section_id)
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')
    section.delete()
    sections = Section.objects.all()
    context = {'sections': section}
    return redirect('section')

def mens_watches(request):
    mens_watches_category = Category.objects.get(category_name="Men's watch")
    mens_watches_products = Product.objects.filter(category=mens_watches_category,deleted=False)
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_price = request.GET.get('price')
    selected_subcategory = request.GET.get('sub_category')
    if selected_brand:
        mens_watches_products = mens_watches_products.filter(product_name=selected_brand)
    if selected_color:
        mens_watches_products = mens_watches_products.filter(color=selected_color)
    if selected_subcategory:
        # Filter for products with the selected subcategory
        mens_watches_products = mens_watches_products.filter(Sub_category__sub_category_name=selected_subcategory)
    if selected_price:
        price_ranges = {
            "price1": (0, 500),
            "price2": (500, 1000),
            "price3": (1000, 5000),
            "price4": (5000, 10000),
            "price5": (10000, 25000),
            "price6": (25000, 50000),
            "price7": (50000, 1000000) 
        }
        if selected_price in price_ranges:
            price_range = price_ranges[selected_price]
            # Filter for products with prices within the selected price range
            mens_watches_products = mens_watches_products.filter(price__range=price_range)
    unique_colors = Product.objects.values('color').annotate(count=Count('color')).order_by('color')
    products = Product.objects.values('product_name').distinct()
    subcategories = Sub_category.objects.values('sub_category_name').distinct()
    for product in mens_watches_products:
        discounted_price = None
        if product.category.category_offer:
          if product.category.category_offer:
            discounted_price = (product.price - (product.price*product.category.category_offer/100))
        # Calculate offer price based on the product_offer
        offer_price=None
        if product.product_offer:
            offer_price = product.price - (product.price * (product.product_offer / 100))
        # Assign the calculated values to the product
        product.discounted_price = discounted_price
        product.offer_price = offer_price
    # Fetch unique colors and subcategories
    unique_colors = Product.objects.values('color').annotate(count=Count('color')).order_by('color')
    subcategories = Sub_category.objects.values('sub_category_name').distinct()
    context = {
        'mens_watches_products': mens_watches_products,
        'unique_colors': unique_colors,
        'products': products,
        'subcategories': subcategories,
    }
    return render(request, 'mens.html', context)


def womens_watches(request):
    womens_watches_category = Category.objects.get(category_name="womens watch")
    womens_watches_products = Product.objects.filter(category=womens_watches_category,deleted=False)
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_price = request.GET.get('price')
    selected_subcategory = request.GET.get('sub_category')
    if selected_brand:
        womens_watches_products = womens_watches_products.filter(product_name=selected_brand)
    if selected_color:
        womens_watches_products = womens_watches_products.filter(color=selected_color)
    if selected_subcategory:
        # Filter for products with the selected subcategory
     womens_watches_products = womens_watches_products.filter(Sub_category__sub_category_name=selected_subcategory)
    if selected_price:
        price_ranges = {
            "price1": (0, 500),
            "price2": (500, 1000),
            "price3": (1000, 5000),
            "price4": (5000, 10000),
            "price5": (10000, 25000),
            "price6": (25000, 50000),
            "price7": (50000, 1000000) 
        }
        if selected_price in price_ranges:
            price_range = price_ranges[selected_price]
            # Filter for products with prices within the selected price range
            womens_watches_products = womens_watches_products.filter(price__range=price_range)
    unique_colors = Product.objects.values('color').annotate(count=Count('color')).order_by('color')
    products = Product.objects.values('product_name').distinct()
    subcategories = Sub_category.objects.values('sub_category_name').distinct()
    for product in womens_watches_products:
        discounted_price = None
        if product.category.category_offer:
          if product.category.category_offer:
            discounted_price = (product.price - (product.price*product.category.category_offer/100))
        # Calculate offer price based on the product_offer
        offer_price=None
        if product.product_offer:
            offer_price = product.price - (product.price * (product.product_offer / 100))
        product.discounted_price = discounted_price
        product.offer_price = offer_price
    context = {
        'womens_watches_products': womens_watches_products,
        'products': products,
        'unique_colors': unique_colors,
        'subcategories': subcategories,
    }
    return render(request, 'womens.html', context)

#coupon
@never_cache
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
def coupon(request):
    if 'admin' in request.session:
        coupons = Coupon.objects.all().order_by('id')
        context = {'coupons': coupons}
        return render(request, 'coupon.html', context)
    else:
        return redirect('admin')

def add_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('Couponcode')
        discount_price = request.POST.get('dprice')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')
        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            messages.error(request, 'Coupon with this code already exists.')
            return redirect('coupon')
        if float(discount_price) < 0:
            messages.error(request, 'Discount price cannot be less than 0')
            return redirect('coupon')
        coupon = Coupon(coupon_code=coupon_code, discount_price=discount_price, minimum_amount=minimum_amount, expiry_date=expiry_date)
        coupon.save()
        return redirect('coupon')

def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        usedcoupon  = Coupon.objects.get(coupon_code = coupon_code)
        usedcouponid = usedcoupon.id
        user = request.user
        try:
            couponuser = CustomUser.objects.get(email=user)
            userid = couponuser.id  
        except CustomUser.DoesNotExist:
            messages.error(request, "Customer not found.")
            return redirect('cart')
        cart_items = Cart.objects.filter(user=user)
        subtotal = 0
        shipping_cost = 10
        total_dict = {}
        coupons = Coupon.objects.all()
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
                cart_item.quantity = cart_item.product.stock
                cart_item.save()
            if cart_item.product.category.category_offer:
                item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            elif cart_item.product.product_offer:
                item_price = (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
            else:
                item_price = cart_item.product.price * cart_item.quantity
                total_dict[cart_item.id] = item_price
                subtotal += item_price
        try:
            usedCoupon = UsedCoupon.objects.get(user_id=userid , coupon_id = usedcouponid )
            messages.error(request, "Coupon already applied")
            total = subtotal + shipping_cost
        except UsedCoupon.DoesNotExist:
            # If the coupon code is valid and hasn't been used by the user, apply it here
            try:
                coupon = Coupon.objects.get(coupon_code=coupon_code)
                if subtotal >= coupon.minimum_amount:
                    messages.success(request, 'Coupon applied successfully')
                    # UsedCoupon.objects.create(user_id=userid, coupon=coupon)  # Create a record that coupon is used
                    request.session['discount'] = coupon.discount_price
                    total = subtotal - coupon.discount_price + shipping_cost
                else:
                    messages.error(request, 'Coupon not available for this price')
                    total = subtotal + shipping_cost
            except Coupon.DoesNotExist:
                messages.error(request, 'Invalid coupon code')
                total = subtotal + shipping_cost
        for cart_item in cart_items:
            cart_item.total_price = total_dict.get(cart_item.id, 0)
            cart_item.save()
        context = {
            'cart_items': cart_items,
            'subtotal': subtotal,
            'total': total,
            'coupons': coupons,
            'discount_amount': request.session.get('discount',0),
        }
        return render(request, 'cartt.html', context)
    return redirect('cartt')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_coupon(request,id):
    if 'admin' in request.session:
        try:
            coupon = Coupon.objects.get(id=id)
        except Section.DoesNotExist:
            return render(request, 'subcategory_not_found.html')
        context = {'coupon': coupon}
        return render(request, 'edit_coupon.html', context)
    else:
        return redirect ('admin')
    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_coupon(request, id):
    # Use get_object_or_404 to retrieve the coupon or return a 404 page if it doesn't exist
    coupon = get_object_or_404(Coupon, id=id)
    if request.method == 'POST':
        coupon_code = request.POST.get('Couponcode')
        discount_price = request.POST.get('price')
        minimum_amount = request.POST.get('amount')
        expiry_date = request.POST.get('date')
        # Check if coupon_code and discount_price are not null before updating
        if coupon_code:
            coupon.coupon_code = coupon_code
        if discount_price:
            coupon.discount_price = discount_price
        coupon.minimum_amount = minimum_amount
        coupon.expiry_date = expiry_date
        coupon.save()  # Save the updated coupon object here
        return redirect('coupon')
    context = {'coupon': coupon}
    return render(request, 'edit_coupon.html', context)
def delete_coupon(request,id):
    try:
        coupon= Coupon.objects.get(id=id)
    except Coupon.DoesNotExist:
        return render(request, 'category_not_found.html')
    coupon.delete()
    coupons = Coupon.objects.all()
    context = {'coupons': coupons}
    return redirect('coupon')

# user-side search 
@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def search(request):
    query = request.GET.get('q', '')
    products = Product.objects.select_related('category', 'section').all()
    products_with_offers = []  # This will hold our product dictionaries

    for product in products:
        # Calculate category offer and product offer
        category_offer = product.category.category_offer if product.category.category_offer else 0
        product_offer = product.product_offer if product.product_offer else 0

        # Calculate discount and offer prices
        discount_amount = (product.price * category_offer) / 100 if category_offer else 0
        offer_price_amount = (product.price * product_offer) / 100 if product_offer else 0

        # Use the highest priority offer
        final_price = product.price - max(discount_amount, offer_price_amount)

        # Create a dictionary for each product with all necessary data
        product_data = {
            'id': product.id,
            'product_name': product.product_name,
            'description': product.description,
             'category': product.category.category_name,  # Use the correct field name from the Category model
             'stock': product.stock,
             'price': product.price,
             'image_url': product.image.url,
             'section': product.section.name if product.section else '',  # Handling a possible None value
             'color': product.color,
             'product_offer': product_offer,
            'discounted_price': product.price - discount_amount if category_offer else None,
             'offer_price': product.price - offer_price_amount if product_offer else None,
             'final_price': final_price,
}
        products_with_offers.append(product_data)

    # If there's a query, filter the products list
    if query:
        products_with_offers = [
            product for product in products_with_offers
            if query.lower() in product['product_name'].lower() or query.lower() in product['description'].lower()
        ]

    context = {
        'products': products_with_offers,
    }

    # Now we render the template with the context containing product dictionaries
    return render(request, 'search.html', context)
def search_suggestions(request):
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(product_name__icontains=query)[:5]  # Limiting to 5 suggestions
        suggestions = [product.product_name for product in products]
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)


def proceed_to_pay(request):
    cart = Cart.objects.filter(user=request.user)
    total = 0
    shipping = 10
    subtotal=0
    for cart_item in cart:
        if cart_item.product.category.category_offer:
            item_price = (cart_item.product.price - (cart_item.product.price*cart_item.product.category.category_offer/100)) * cart_item.quantity
            subtotal += item_price
        elif cart_item.product.product_offer:
            itemprice =  (cart_item.product.price - (cart_item.product.price * cart_item.product.product_offer/100)) * cart_item.quantity
            subtotal=subtotal+itemprice
        else:
            itemprice = (cart_item.product.price) * (cart_item.quantity)
            subtotal = subtotal + itemprice
    for item in cart:
        discount = request.session.get('discount', 0)
    total=subtotal+shipping 
    if discount:
        total -= discount
    return JsonResponse({
        'total' : total

    })

def wallet(request):
    user = request.user
    customer=CustomUser.objects.get(email=user)
    wallet_transactions = Wallet.objects.filter(user=user).order_by('-created_at')
    context = {
        'wallet_transactions': wallet_transactions,
        'customer':customer,
    }
    return render(request, 'wallet.html', context)


# admin-side search
def admin_search(request):
    query=request.GET.get('q','')
    if query:
        orders=Order.objects.filter(
            models.Q(user__name__icontains=query)
        )
        search_results=orders
    context = {
        'orders': orders,
        'search_results':  search_results,
    }
    return render(request,'admin_search.html',context)

def return_order(request,id):
    user=request.user
    usercustm=CustomUser.objects.get(email=user)
    order = Order.objects.get(id=id)
    order.status='returned'
    order.save()
    restock_products(order) 
    if order.status == 'returned' and order.payment_type == 'cod':
        wallet=Wallet.objects.create(
            user=user,
            order=order,
            amount=order.amount,
            status='Credited',
        )
        wallet.save()
        Order_item_amount=Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    elif order.status=='returned' and order.payment_type=='razorpay':
        wallet=Wallet.objects.create(
        user=user,
        order= order,
        amount= order.amount,
        status='Credited',
        )
        wallet.save()
        order.status='returned'
        order.save()
        Order_item_amount=Decimal(order.amount)
        usercustm.wallet_bal+=Order_item_amount
        usercustm.save()
    return redirect('order_details',id)

def invoice(request, id):
    # 1. Fetch the order and items
    user = request.user
    orders = Order.objects.filter(id=id)
    order_items = OrderItem.objects.filter(order=id)
    discount_amount = request.session.get('discount', 0)
    for order in orders:
        address= order.address
        for item in order_items:
            product_offer = None
            if item.product.category.category_offer:
                product_offer = item.product.category.category_offer
            # 2. Render the order and items to an HTML template
            rendered = render_to_string('invoice.html', {'order': order, 'item': item, 'address':address, 'discount_amount': discount_amount,  'product_offer': product_offer,})
            # 3. Convert the rendered HTML to PDF
            output = io.BytesIO()
            pdf = pisa.CreatePDF(rendered, output)
            pdf_data = output.getvalue()
            # 4. Send the PDF as an email attachment
            msg = MIMEMultipart()
            msg['From'] = 'heandshe2206@gmail.com'
            msg['To'] = order.user.email
            msg['Subject'] = 'Invoice from he & She'
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(pdf_data)
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', 'attachment; filename=invoice.pdf')
            msg.attach(attachment)
            try:
                smtp_server = 'smtp.gmail.com'
                smtp_port = 587
                smtp_username = 'heandshe2206@gmail.com'
                smtp_password = 'nyxbksyvujbbkmdh'
                server = smtplib.SMTP(smtp_server, smtp_port)
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                server.quit()
            except Exception as e:
                return HttpResponse(f'Email sending failed: {str(e)}')
    return HttpResponse('Emails sent successfully!')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def banner(request):
    if 'admin' in request.session:
        banner=Banner.objects.all()
        context = {
            'banner':banner,
    }
        return render(request,'banner.html',context)
    else:
        return redirect('admin')

def add_banner(request):
    if 'admin' in request.session:  
        if request.method == 'POST':
            description = request.POST.get('description')
            image = request.FILES.get('image')
            banner = Banner(description=description, image=image)
            banner.save()
            return redirect('banner') 
        return render(request,'add_banner.html') 
    else:
        return redirect('admin')

@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def edit_banner(request, banner_id):
    if 'admin' in request.session:
        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
        
            return render(request, 'product_not_found.html')
        context = {
            'banner': banner,  
        }
        return render(request, 'edit_banner.html', context)
    else:
        return redirect('admin')

   
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def update_banner(request,banner_id):
    banner= Banner.objects.get(id=banner_id)
    if request.method == 'POST':
        banner.description = request.POST.get('description')
        image = request.FILES.get('image')
        if image:
            banner.image = image
        banner.save()
        return redirect('banner')
    else:
        context = {
            'banner': banner,
        }
        return render(request, 'banner.html', context)

def delete_banner(request,banner_id):
    print(banner_id)
    try:
        banner = Banner.objects.get(id=banner_id)
        banner.delete()
    except Banner.DoesNotExist:
        return render(request, 'category_not_found.html')
    return redirect('banner')

# Create bar chart function
def create_bar_chart(labels, data, title):
    plt.figure(figsize=(8, 6))
    plt.bar(labels, data, color='skyblue')
    plt.xlabel('Products')
    plt.ylabel('Amount')
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'

# pie chart function
def create_pie_chart(labels, data, title):
    plt.figure(figsize=(8, 8))
    plt.pie(data, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(title)
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()
    return f'data:image/png;base64,{chart_image}'


def report_generator(request, orders):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    story = []

    data = [["Order ID", "Total Quantity", "Product IDs", "Product Names", "Amount"]]

    for order in orders:
        # Retrieve order items associated with the current order
        order_items = OrderItem.objects.filter(order=order)
        total_quantity = sum(item.quantity for item in order_items)

        if order_items.exists():
            product_ids = ", ".join([str(item.product.id) for item in order_items])
            product_names = ", ".join([str(item.product.product_name) for item in order_items])
        else:
            product_ids = "N/A"
            product_names = "N/A"

        data.append([order.id, total_quantity, product_ids, product_names, order.amount])

    # Create a table with the data
    table = Table(data, colWidths=[1 * inch, 1.5 * inch, 2 * inch, 3 * inch, 1 * inch])

    # Style the table
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(table_style)

    # Add the table to the story and build the document
    story.append(table)
    doc.build(story)

    buf.seek(0)
    return FileResponse(buf, as_attachment=True, filename='orders_report.pdf')

def report_pdf_order(request):
    if request.method == 'POST':
        from_date = request.POST.get('from_date')
        to_date = request.POST.get('to_date')
        try:
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        except ValueError:
            return HttpResponse('Invalid date format.')
        orders = Order.objects.filter(date__range=[from_date, to_date]).order_by('-id')
        return report_generator(request, orders)

def chart_demo(request):
    orders = Order.objects.order_by('-id')[:5]
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(order.amount)
    context = {
        'labels': json.dumps(labels),
        'data': json.dumps(data),
    }
    return render(request, 'chart_demo.html', context)


def contact(request):
    context = {}  
    if request.method=='POST':
        user=request.user
        message = request.POST.get('message')
        
        # Save the message to the database
        contact = Contact(user=user,message=message)
        contact.save()
        messages.success(request,'Thank you for contacting us!')

        return redirect('contact') 
    return render(request,'contact.html',context)



def adminside_message(request):
    customer_messages=Contact.objects.all()
    context={
        'customer_messages':customer_messages
    }
    return render(request,'adminside_message.html',context)


def reply(request):
    if request.method == 'POST':
        user_email = request.POST.get('email')
        message_content = request.POST.get('message')

        subject = 'Message from He & She'
        from_email = 'heandshe2206@gmail.com'
        to_email = user_email

        # Create the MIME message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message_content, 'plain'))

        # try:
        smtp_server = 'smtp.gmail.com'
        smtp_port = 587
        smtp_username = 'heandshe2206@gmail.com'
        smtp_password = 'nyxbksyvujbbkmdh'
        # Connect to the server and send the email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()

    messages.success(request, 'Email sent successfully.')
    return redirect('adminside_message')
 