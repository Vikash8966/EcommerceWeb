from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, auth
from django.http import JsonResponse
from .models import *
from .utils import cookieCart, cartData, guestCheckout

import json
import datetime

# Create your views here.

def loginUser(request):
     page = 'login'
     # restricts logedin user to visit login pg
     if request.user.is_authenticated:
          return redirect('logout')

     if request.method == 'POST':
          username = request.POST['username']
          password = request.POST['password']
          # to cath exception
          try:
               # queriying the user
               user = User.objects.get(username=username)
          except:
               messages.error(request, 'Username does not exist')
          # fetching user data
          user = authenticate(request, username=username, password=password)
          if user is not None:
               auth.login(request, user)
               return redirect('store')
          else:
              messages.error(request, 'Username or password is incorrect')
     return render(request, 'store/login_register.html')


def logoutUser(request):
    logout(request)
    messages.info(request, 'sucessfully logged out')
    return redirect('login')


def registerUser(request):
     page = 'register'

     if request.method == 'POST':
          print("*****Yes Post")
          first_name = request.POST.get('first_name')
          last_name = request.POST.get('last_name')
          username = request.POST.get('username')
          email = request.POST.get('email')
          password1 = request.POST.get('password1')
          password2 = request.POST.get('password2')
          # to bverify both password
               
          if password1==password2:
               # creating an user obj
               # check if email and name already exist
               if User.objects.filter(username=username).exists():
                    messages.success(request, "username exist, please choose different username")
               if User.objects.filter(email=email).exists():
                    messages.success(request, "user email already exist, please choose different email")
               else:
                    user = User.objects.create_user(username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                    user.username = user.username.lower()
                    user.save()
                    print("User created")
                    login(request, user)
               return redirect('store')
          else:
               messages.success(request, "Password doesn't match")
          
     context = {'page': page,
                }
     return render(request, 'store/login_register.html', context)


# Create your views here.
def store(request):
     data = cartData(request)
     cartItems = data['cartItems']
     products = Product.objects.all()
     context = {'products':products, 'cartItems':cartItems}
     print("UserName: *****", request.user.username)
     return render(request, 'store/store.html', context)

def cart(request):
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']
     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/cart.html', context)

def checkout(request):
     data = cartData(request)
     cartItems = data['cartItems']
     order = data['order']
     items = data['items']
          
     context = {'items':items, 'order':order, 'cartItems':cartItems}
     return render(request, 'store/checkout.html', context)

def updateItem(request):
     #return json obj as a dict
     data = json.loads(request.body)
     productId = data['productId']
     action = data['action']
     
     print('Action: ', action)
     print('productId:', productId)
     
     customer = request.user.customer
     # querysets
     product = Product.objects.get(id=productId)
     order, created = Order.objects.get_or_create(customer=customer, complete=False)
     orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)
     
     if action == 'add':
          orderItem.quantity += 1
     elif action == 'remove':
          orderItem.quantity -= 1
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
          customer, order = guestCheckout(request, data)
     
     print("DATA: ", data)
     total = float(data['form']['total'])
     order.transaction_id = transaction_id
     
     # for security payment opt
     if total == float(order.get_cart_total):
          order.complete = True
     print("total: ", type(total),"order.get_cart_total: ", type(order.get_cart_total), "Order Complete: ", order.complete, "order.transaction_id: ", order.transaction_id)
     order.save()
     
     if order.shipping==True:
          ShippingAddress.objects.create(
               customer=customer,
               order=order,
               address=data['shipping']['address'],
               city = data['shipping']['city'],
               state = data['shipping']['state'],
               zipcode = data['shipping']['zipcode'],
          )
     
     return JsonResponse("Payment Completed ..", safe=False) 