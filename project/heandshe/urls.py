from django.urls import path
from . import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns=[
    path('base/',views.base,name='base'),
    path('',views.home,name='home'),
    path('adminlogin/',views.adminlogin,name='adminlogin'),
    path('dashboard/',views.dashboard,name='dashboard'),  
    path('admin_logout/',views.admin_logout,name='admin_logout'),
    path('customer/',views.customers,name='customer'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.user_login,name='login'),
    path('block-customer/<int:customer_id>/', views.block_customer, name='block_customer'),
    path('unblock-customer/<int:customer_id>/', views.unblock_customer, name='unblock_customer'),

    # category
    path('category/',views.category,name='category'),
    path('add_category/',views.add_category,name='add_category'),
    path('category/<int:id>/update_category/',views.update_category,name='update_category'),
    path('category/<int:category_id>/edit_category/', views.edit_category, name='edit_category'),
    path('category/<int:category_id>/delete_category/',views.delete_category,name='delete_category'),



    # sub category
    path('sub_category/', views.sub_category, name='sub_category'),
    path('add_sub_category/', views.add_sub_category, name='add_sub_category'),
    path('category/<int:sub_category_id>/update_sub_category/', views.update_sub_category, name='update_sub_category'),
    path('category/<int:sub_category_id>/edit_sub_category/', views.edit_sub_category, name='edit_sub_category'),
    path('category/<int:sub_id>/delete_sub_category/',views.delete_sub_category,name='delete_sub_category'),
   

    # products
    path('product/',views.product,name='product'),
    path('add_product/',views.add_product,name='add_product'),
    path('product/<int:product_id>/edit_product/', views.edit_product, name='edit_product'),
    path('product/<int:product_id>/update_product/',views.update_product,name='update_product'),
    path('product/<int:product_id>/delete_product/',views.delete_product,name='delete_product'),
    
    path('verify_otp/',views.verify_signup,name='verify_signup'),
    path('logout/',views.logout,name='logout'),

    path('product_details/<int:id>/',views.userproductpage,name='user_product'),
    path('shop/',views.shop,name='shop'),

    # profile
    path('profile/',views.profile,name='profile'),
    path('update_profile/',views.update_profile,name='update_profile'),



    # address
    path('address/',views.address,name='address'),
    path('add_address/',views.add_address,name='add_address'),
    path('edit_address/<int:id>/', views.edit_address, name='edit_address'),
    path('delete_address/<int:id>/', views.delete_address, name='delete_address'),


    path('changepassword/',views.changepassword,name='changepassword'),


    #wishlist
    path('wishlist/',views.wishlist, name='wishlist'),
    path('addtowishlist/<int:id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove_from_wishlist/<int:wishlist_item_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    

    # cart
    # path('cart/',views.cart,name='cart'),
    path('cartt/',views.cartt,name='cartt'),
    path('remove_from_cart/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:productId>/', views.update_cart, name='update_cart'),
    path('add_to_cart/<int:id>/', views.add_to_cart, name='add_to_cart'),


    path('check_out/',views.check_out,name='check_out'),
    path('shipping_address/',views.shipping_address,name='shipping_address'),
    path('order_placed/',views.order_placed,name='order_placed'),
    path('success/',views.success,name='success'),



    # admin order
    path('order/',views.order,name = 'order'),
    path('update_order/', views.updateorder,name='update_order'),


    # costumer
    path('order_details/<int:id>',views.order_details,name='order_details'),
    path('cancel-order/<int:id>/', views.cancel_order,name='cancel_order'),
    path('return_order/<int:id>/', views.return_order, name='return_order'),
    path('customer_order/',views.customer_order,name='customer_order'),

    # forgot password
    path('forgot_password/', views.forgot_password,name='forgot_password'),
    path('reset_password/', views.reset_password,name='reset_password'),


    # variation
    # path('variations/',views.variations,name='variations'),
    # path('variations/<int:product_id>/',views.variations,name='variations'),
    # path('delete_variation/<int:id>/', views.delete_variation, name='delete_variation'),
    # path('edit_variation/<int:id>/',views.edit_variation,name='edit_variations' ),
    # path('update_variations/<int:id>/',views.update_variation,name='update_variation'),
    # path('add_variations/',views.add_variation,name='add_variation'),
    # path('display_variations/',views.display_variations,name='display_variations'),


   #section
    path('section/',views.section, name = 'section'),
    path('add_section/',views.add_section,name= 'add_section'),
    path('update_section/<int:id>/update_section/', views.update_section, name='update_section'),
    path('delete_section/<int:section_id>/delete/', views.delete_section, name='delete_section'),
    path('edit_section/<int:section_id>/edit/', views.edit_section, name='edit_section'),

    #men
    path('mens/',views.mens_watches,name='mens'),
    #women
    path('womens/',views.womens_watches,name='womens'),
    path('contact/',views.contact,name='contact'),

    #coupon
    path('coupon/',views.coupon,name ='coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
    path('update_coupon/<int:id>/',views.update_coupon, name='update_coupon'),
    path('edit_coupon/<int:id>/', views.edit_coupon, name='edit_coupon'),
    path('delete_coupon/<int:id>/',views.delete_coupon, name='delete_coupon'),

    # search
    path('search/',views.search,name='search'),
    # admin_search
    path('admin_search/',views.admin_search,name='admin_search'),
   

   #razorpay
    path('proceed-to-pay',views.proceed_to_pay,name='proceed_to_pay'),
    path('razorpay/<int:address_id>/',views.razor_pay,name='razorpay'),

    # wallet
    path('wallet/',views.wallet,name='wallet'),
    # invoice
    path('invoice/<int:id>/',views.invoice,name='invoice'),

    # banner
    path('banner/',views.banner,name='banner'),
    path('add_banner/',views.add_banner,name='add_banner'),
    path('edit_banner/<int:banner_id>/',views.edit_banner,name='edit_banner'),
    path('update_banner/<int:banner_id>/',views.update_banner,name='update_banner'),
    path('delete_banner/<int:banner_id>/',views.delete_banner,name='delete_banner'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)