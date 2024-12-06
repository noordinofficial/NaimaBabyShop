from ast import Or
import email
from itertools import product
import re
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout, get_backends
from django.contrib import messages
from .models import *
import json
import datetime
from .utils import cookieCart, cartData, guestOrder
from .forms import OrderForm, CreateUserForm
# from .filters import OrderFilter
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth
from django.shortcuts import render, get_object_or_404
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import requests
from requests.auth import HTTPBasicAuth
from .utils import generate_password 
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.shortcuts import redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
import requests
from urllib.parse import urlencode
from django.db.models import Q
import google.generativeai as genai
import os
from django.conf import settings

from dotenv import load_dotenv
load_dotenv()

def chatbot(request):
    if request.method == 'POST':
        user_message = request.POST.get('message')
        
        # Configure the API key
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 4192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config=generation_config,
            system_instruction="Assume you are a chatbot(be brief in your responses) for an ecommerce site called little wonders that sells baby and kids products, the store only has 21 products in 7 categories for now and here is their categories and descriptions of each \"Travel\nBaby Bike\n\nDescription: A small blue bike designed for toddlers, with three wheels for stability.\nPrice: Ksh.1300.00\nVisual: Blue frame with grey wheels and white accents.\nWrap Carrier\n\nDescription: A grey baby wrap carrier, ideal for holding infants close to the body.\nPrice: Ksh.2000.00\nVisual: Grey fabric, comfortable fit, worn by a parent holding a baby.\nRocking Horse\n\nDescription: A grey rocking horse toy with a plush body and wooden rockers.\nPrice: Ksh.1000.00\nVisual: Grey, plush material with white polka dots, wooden rocking base.\nClothing\nRing Unicorn\n\nDescription: Unicorn-themed hair rings.\nPrice: Ksh.800.00\nVisual: Colorful unicorn heads attached to hair ties, mainly pink and white.\nBlue Jumper\n\nDescription: A blue jumper for kids with a hood.\nPrice: Ksh.1000.00\nVisual: Blue fabric with small white patterns, hooded.\nKids Socks\n\nDescription: Colorful socks for children.\nPrice: Ksh.1000.00\nVisual: Various colors, each pair with a different design.\nToys\nPlaytime Fox\n\nDescription: A plush fox toy with various accessories.\nPrice: Ksh.300.00\nVisual: A cute fox with colorful attire, including a small handbag.\nCar Toy\n\nDescription: A red toy car.\nPrice: Ksh.500.00\nVisual: Small, sleek red car model.\nBarrel Toy\n\nDescription: A small brown plush bear.\nPrice: Ksh.360.00\nVisual: Brown bear sitting upright, simple design.\nDiapering\nBaby Float-Tube\n\nDescription: An inflatable tube for babies to float in water.\nPrice: Ksh.600.00\nVisual: Green inflatable tube with a baby inside.\nBaby Wipes\n\nDescription: Pack of baby wipes.\nPrice: Ksh.150.00\nVisual: White and blue packaging with a baby on the front.\nBaby Nappies\n\nDescription: Disposable nappies for babies.\nPrice: Ksh.400.00\nVisual: Pack of nappies, white and green packaging with a baby image.\nHealth\nKid's Immune\n\nDescription: Immunity booster for kids.\nPrice: Ksh.2500.00\nVisual: Colorful packaging with images of fruits and animals.\nOmega 3\n\nDescription: Omega 3 supplement for kids.\nPrice: Ksh.2000.00\nVisual: White bottle with a blue and red label.\nChildren's DHA\n\nDescription: DHA supplement for kids.\nPrice: Ksh.1400.00\nVisual: Blue bottle with colorful labeling.\nSummer Sales(Get 20% off on all baby clothes)\n\n\nCotton PJs Blue Stripe\n\nDescription: Cotton pajamas with blue stripes.\nPrice: Ksh.5400.00\nVisual: Blue and white striped pajamas.\nSwim Wear Set\n\nDescription: Two-piece swimwear set.\nPrice: Ksh.4300.00\nVisual: Dark top with colorful hearts, pink bottom.\nVeggie PJs\n\nDescription: Pajamas with vegetable prints.\nPrice: Ksh.4350.00\nVisual: Dark pajamas with colorful vegetable prints.\nNew Arrivals(Check out our latest baby toys)\nElephant Duck\n\nDescription: Duck-shaped float with an elephant toy.\nPrice: Ksh.1720.00\nVisual: Yellow duck float with a small blue elephant.\nMagic Rocket\n\nDescription: Colorful stacking toy in the shape of a rocket.\nPrice: Ksh.1230.00\nVisual: Rainbow-colored stackable pieces forming a rocket.\nLearning Watch\n\nDescription: A blue educational watch for kids.\nPrice: Ksh.800.00\nVisual: Blue watch with an interactive screen and buttons.\"",
        )

        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        "who is the president us",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "I can't help you with that! I'm just a chatbot here to answer your questions about Little Wonders and our baby and kids products in the following categories: Clothing, Toys, Bags, Diapering, and Health.  \n\nIs there anything you'd like to know about the products we sell? 😊 \n",
                    ],
                },
            ]
        )

        response = chat_session.send_message(user_message)

        return JsonResponse({'response': response.text})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
    

def google_login(request):
    # Step 2: Redirect to Google's OAuth 2.0 server
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': request.build_absolute_uri('/google/callback/'),
        'scope': 'openid email profile',
        'response_type': 'code',
        'access_type': 'offline',
        'prompt': 'consent',
    }
    url = f'https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}'
    return redirect(url)


def google_callback(request):
    # Step 3: Handle the callback from Google
    code = request.GET.get('code')
    token_url = 'https://oauth2.googleapis.com/token'
    token_data = {
        'code': code,
        'client_id': settings.GOOGLE_CLIENT_ID,
        'client_secret': settings.GOOGLE_CLIENT_SECRET,
        'redirect_uri': request.build_absolute_uri('/google/callback/'),
        'grant_type': 'authorization_code',
    }
    token_r = requests.post(token_url, data=token_data)
    token = token_r.json().get('access_token')
    userinfo_url = 'https://www.googleapis.com/oauth2/v3/userinfo'
    userinfo_r = requests.get(userinfo_url, params={'access_token': token})
    userinfo = userinfo_r.json()

    # Step 4: Retrieve or create the user based on the response
    users = User.objects.filter(email=userinfo['email'])
    if users.count() == 1:
        user = users.first()
    elif users.count() == 0:
        # Assuming your User model has an email field; adjust as necessary
        user = User.objects.create(email=userinfo['email'], username=userinfo.get('name', userinfo['email']))
    else:
        # Handle multiple users with the same email
        # This is a basic example; consider a more sophisticated approach
        user = users.first()  # Arbitrarily logging in the first user found
        # Consider logging this issue or notifying an admin

    # Log the user in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Specify the correct backend if necessary

    # Redirect the user to the homepage or another appropriate page
    return redirect('/')

def get_oauth_token():
    consumer_key = 'twaWO70bUBXZbZKA0ii1I4xAzsssldFZBhoA4ApfUR7PUw6G'
    consumer_secret = 'wAeJHQQ35c6EwanAZIfqPKFEzWRhmoPJEUG4nqpuClH96dSbcXjt0cd67lBcShgl'
    api_url = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(api_url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    if response.status_code == 200:
        json_response = response.json()
        return json_response["access_token"]
    else:
        return None

@csrf_exempt
def process_payment(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_number = data['phoneNumber']
        amount = data['amount']
        if phone_number.startswith("07"):
            phone_number = "254" + phone_number[1:]

	

        # Generate password
        shortcode = "174379"
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        password = generate_password(shortcode, passkey)
        
        # Prepare M-Pesa transaction
		
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')		
        transaction_data = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": shortcode,
            "PhoneNumber": phone_number,
            "CallBackURL": "https://yourdomain.com/mpesa/callback",
            "AccountReference": "NaimaBabyShop",
            "TransactionDesc": "Payment of X"
        }
		
      
        # Obtain OAuth token
        access_token = get_oauth_token()
        if not access_token:
            return JsonResponse({"success": False, "message": "Failed to obtain OAuth token."})
			
        
        # Send transaction to M-Pesa
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", json=transaction_data, headers=headers)
        print(response.text)
        if response.status_code == 200:
            return JsonResponse({"success": True, "message": "Transaction initiated successfully."})
        else:
            return JsonResponse({"success": False, "message": "Failed to initiate transaction."})

def registerPage(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()# Password is hashed here before saving to the database
            backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user, backend = backend)
            username = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('shop')
        else:
            # Print form errors to the console for debugging
            print(form.errors)
            messages.error(request, "Unsuccessful registration. Invalid information.")
    else:
        form = CreateUserForm()
    
    context = {'form': form}
    return render(request, 'shop/register.html', context)


def loginPage(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)

		# Always create the form, even if the authentication fails
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = auth.authenticate(request, username=username, password=password)

			if user is not None:
				auth.login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("shop")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	else:
		form = AuthenticationForm()

	return render(request=request, template_name="shop/login.html", context={"login_form":form})

def logoutUser(request): 
	auth.logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect('shop')

def shop(request):
    data = cartData(request)
    cartItems = data['cartItems']

    order = data['order']
    items = data['items']

    query = request.GET.get('q', '')  # Capture the search query parameter
    if query:
        # Filter products based on the query
        products = Product.objects.filter( Q(name__icontains=query) | Q(category__icontains=query))
        is_search = True
    else:
        # If no query, retrieve all products
        products = Product.objects.all()
        is_search = False
    categories = Product.objects.values_list('category', flat=True).distinct()
    fproducts = Product.objects.all()

    context = {
        'fproducts': fproducts,
        'products': products, 
        'cartItems': cartItems,
        'is_search': is_search,
        'query': query,
        'categories': categories
    }
    return render(request, 'shop/store.html', context)   

def cart(request):
	data = cartData(request)
	cartItems = data['cartItems']

	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'shop/cart.html', context)
def checkout(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items': items, 'order': order, 'cartItems': cartItems}
	return render(request, 'shop/checkout.html', context)


def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)
	
	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)


def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)

	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id
	
	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)
	
	return JsonResponse('Payment complete!', safe=False)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)
    recommended_products = similar_products[:6]


    context = {
        'product': product,
        'recommended_products': recommended_products
    }

    return render(request, 'shop/product_detail.html', context)