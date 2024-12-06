from django.urls import path
from . import views
from allauth.socialaccount.providers.google.views import oauth2_login
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from django.urls import path
from .views import google_login, google_callback
from .views import chatbot





urlpatterns = [
    path('register/', views.registerPage, name="register"),
    path('', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('shop', views.shop, name="shop"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('google/login/', google_login, name='google_login'),
    path('google/callback/', google_callback, name='google_callback'),
    path('chatbot/', chatbot, name='chatbot'),


    
]