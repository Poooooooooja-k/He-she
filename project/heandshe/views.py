from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.cache import cache_control, never_cache
from django.contrib import messages
from .models import  CustomUser
from .models import Category
from .models import Sub_category
from .models import Product
from .models import Images
from .models import Address
from .models import Wishlist
from .models import Cart
from .models import Order
from .models import OrderItem
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


# Create your views here.

def base(request):
    return render(request,'base.html')

def home(request):
    # product=Product.objects.all()
    # # product=Product.objects.filter(category__category_name='category')
    # print(product)
    # context={
    #     'product':product,
    # }
    return render(request,'home.html')

def adminlogin(request):
    if 'email' in request.session:
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
        
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache
def dashboard(request):

    if 'admin' in request.session:
        return render(request,'dashboard.html')
    else:
        return redirect('adminlogin')

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
        # a = request.session.get('email')
        # print(a)
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
    #     return redirect('login')
    
    # return render(request, 'signup.html')


    
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
        # user = CustomUser.objects.create_user(name=name, password=password, email=email,phone_number=phone_number)
        # user.save()

        request.session['email'] =  email
        request.session['otp']   =  message
        messages.success (request, 'OTP is sent to your email')
        print("..............reac")
        return redirect('verify_signup')
    
    return render(request,'signup.html')

    

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
        
            auth.login(request,user)
            messages.success(request, "Signup successful!")
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
    

def user_login(request):
    if request.method == "POST":
        email = request.POST.get('email')  # Use 'email' instead of 'username'
        password = request.POST.get('password')

        # Authenticate against your custom Customer model using email
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Email and password are invalid!')
            return redirect('login')
    return render(request, 'login.html')

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
            # category_id         =request.POST.get('category_id')
            category_name       =   request.POST.get('category_name')
            # description         =   request.POST.get('description')
            # image               =   request.FILES.get('image')
            # offer_description   =   request.POST['offer_details']
            # offer_price         =   request.POST['offer_price']


            category = Category.objects.create(category_name = category_name)
               
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
        category_name = request.POST.get('category_name')
        if category_name:
            category.category_name           =  category_name
        category.description                 =  request.POST.get('description')
        # image                                =  request.FILES.get('image')
        # category.category_offer_description  =  request.POST.get('offer_details')
        # category.category_offer              =  request.POST.get('offer_price')
        # if image:
        #     category.image = image
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
    except Category.DoesNotExist:
        return render(request, 'category_not_found.html')

    category.delete()

    categories = Category.objects.all()
    context = {'categories': categories}

    return redirect('category',context)



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


def delete_sub_category(request, sub_id):
    try:
        sub_category = Sub_category.objects.get(id=sub_id)
    except Sub_category.DoesNotExist:
        return render(request, 'category_not_found.html')

    sub_category.delete()

    sub_category = Sub_category.objects.all()
    context = {'categories': sub_category}

    return redirect('sub_category')




@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def product(request):
    if 'admin' in request.session:
        
        products        = Product.objects.all().order_by('id')       
        paginator = Paginator(products, 3)  
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
           
        }
        return render(request, 'product.html', context)
    else:
        return redirect('admin')


@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def add_product(request):
    categories = Category.objects.all()
    if 'admin' in request.session:
        if request.method == 'POST':
            product_name   =  request.POST.get('product_name')
            description    =  request.POST.get('description')
            subcategory_id =    request.POST.get('subcategory_id')
            stock          =  request.POST.get('stock')
            price          =  request.POST.get('price')
            image          =  request.FILES.get('image') 
            
        
            try:
                subcategory_id = Sub_category.objects.get(id=subcategory_id )
                main_category_id = subcategory_id.main_category_id
                print(main_category_id,"..............main category")
                # sub_name   = category.category_name
            except Sub_category.DoesNotExist:
                return HttpResponse("sub Category not found")
            
            product = Product.objects.create(
               product_name = product_name,
               description = description,
               Sub_category= subcategory_id,
               category_id    = main_category_id,
               stock = stock,
               price = price,
               image = image,
               

            )
          
            for image in request.FILES.getlist('image'):
                Images.objects.create(product = product,images=image)

            return redirect('product')

        context = {'categories': categories}
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
        context = {
            'product'    : product,
            'categories' : categories,
        }

        return render(request, 'edit_product.html', context)
    else:
        return redirect('admin')
    
@cache_control(no_cache=True,must_revalidate=True,no_store=True)
@never_cache  
def update_product(request,product_id):
    product = Product.objects.get(id=product_id)
    if request.method == 'POST':
        product.product_name    =   request.POST.get('product_name')
        product.description     =   request.POST.get('description')
        category_name           =   request.POST.get('category')
        category                =   Category.objects.get(category_name=category_name)
        product.category        =   category
        product.stock           =   request.POST.get('stock')
        product.price           =   request.POST.get('price')
        image                   =   request.FILES.get('image')
        
        if image:
            product.image = image
        product.save()
       
        for image in request.FILES.getlist('images'):
            im=Images.objects.create(product=product, images=image)
            print(im)

        return redirect('product') 
    else:
        context = {
            'product': product
        }
    return render(request, 'product.html', context)



def delete_product(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return render(request, 'category_not_found.html')

    product.delete()

    return redirect('product')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache    
def userproductpage(request,id):
    product = Product.objects.filter(id=id) # Get a single product by ID
    
    context = {
        'product': product,
    }

    return render(request, 'product_details.html', context)


def shop(request):
    product=Product.objects.all()
   
    # product=Product.objects.filter(category__category_name='category')
    print(product)
    context={
        'product':product,
    }
    return render(request, 'shop.html',context)




@login_required
@user_passes_test(lambda u: not u.is_staff, login_url='login')
def profile(request):
    user=request.user
    context={
        'user':user,
    }
    return render(request,'profile.html',context)



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
    address=Address.objects.all()
    context={
        'address':address,
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
        address = Address(
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
                messages.success(request, 'Password changed successfully.')
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


def add_to_wishlist(request, id):
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
        else:
            wishlist_item = Wishlist.objects.get(id=wishlist_item_id)
        wishlist_item.delete()
    except Wishlist.DoesNotExist:
        pass
    
    return redirect('wishlist')

@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cart(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user).order_by('id')

    subtotal = 0
    total_dict = {}
    for cart_item in cart_items:
        if cart_item.quantity > cart_item.product.stock:
            messages.warning(request, f"{cart_item.product.product_name} is out of stock.")
            cart_item.quantity = cart_item.product.stock
            cart_item.save()
        else:
            item_price = cart_item.product.price * cart_item.quantity
            total_dict[cart_item.id] = item_price
            subtotal += item_price

    shipping_cost = 10
    total = subtotal + shipping_cost
     

    for cart_item in cart_items:
        cart_item.total_price = total_dict.get(cart_item.id, 0)
        cart_item.save()

        print(cart_items,"........cart item")



    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        
    }


    return render(request, 'cart.html', context)



@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_to_cart(request, id):
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

    return redirect('cart')




def update_cart(request, productId):
    cart_item = None
   
    cart_item = get_object_or_404(Cart, product_id=productId, user=request.user)
    print(cart_item,"....................")
    
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
    
    return redirect('cart')


@never_cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def check_out(request):
    
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal = 0
    for cart_item in cart_items:
        itemprice = (cart_item.product.price) * (cart_item.quantity)
        subtotal = subtotal + itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    address = Address.objects.all()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'total': total,
        'address': address,
        'itemprice': itemprice
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
            return redirect('edit_profile')
        
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
        address.save()
        return redirect('add_address')
        
    else:
        return render(request, 'check_out.html')
    
@login_required
def order_placed(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    subtotal=0
    for cart_item in cart_items:
        itemprice=(cart_item.product.price)*(cart_item.quantity)
        subtotal=subtotal+itemprice
    shipping_cost = 10 
    total = subtotal + shipping_cost if subtotal else 0
    
    

    if request.method == 'POST':
        payment       =    request.POST.get('payment')
        address_id    =    request.POST.get('addressId')
    print(address_id,"  ...................")
    
    if not address_id:
        messages.info(request, 'Input Address!!!')
        return redirect('check_out')
    

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
   



# admin side order

def admin_order_details(request,order_id):
    order = get_object_or_404(Order, id=order_id)

    context = {
        'order': order,
        
    }

    return render(request, 'admin_order_details.html', context)

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
        status = request.POST.get('status')

       
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return redirect('order')  

      
        order.status = status
        order.save()   
        messages.success(request, 'Order status updated successfully.')

        

        return redirect('order') 

    return redirect('admin')


# end admin order



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
    print(orders)
    context ={
         'orders':orders,
        }
    return render(request,'order_details.html',context)


def cancel_order(request,id):
    OrderItem=Order.objects.get(id=id)
    OrderItem.status='cancelled'
    OrderItem.save()
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