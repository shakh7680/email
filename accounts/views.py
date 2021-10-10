from django.http import request
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib import messages
from .models import *
import uuid
from django.conf import settings
from django.core.mail import message, send_mail
from django.contrib import auth
from django.contrib.auth.decorators import  login_required
# Create your views here.


@login_required(login_url='/')
def home(request):
    print(str(uuid.uuid4()))
    return render(request, 'home.html')

def login_attempt(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user_obj = User.objects.filter(username=username).first()
        if user_obj is None:
            messages.success(request, 'User not found.')
            return redirect('/login')
        profile_obj = Profile.objects.filter(user=user_obj).first()

        if not profile_obj.is_verified:
            messages.success(request, 'Profile has not been verified yet. Check your mail')
            return redirect('/login')
        
        user = auth.authenticate(username = username, password = password)
        
        if user is not None:
            auth.login(request, user)
            messages.success(request, 'You are logged in.')
            return redirect('/')
        else:
            messages.success(request, 'Wrong password.')
            return redirect('/login')
        
    return render(request, 'login.html')

def register_attempt(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            if User.objects.filter(username=username).first():
                messages.success(request, 'Username is taken')
                return redirect('/register')
            if User.objects.filter(email=email).first():
                messages.success(request, 'Email is taken')
                return redirect('/register')
            user_obj = User(username=username, email=email)
            user_obj.set_password(password)
            user_obj.save()

            auth_token = str(uuid.uuid4())
            
            profile_obj = Profile.objects.create(user=user_obj, auth_token=auth_token)
            profile_obj.save()
            send_mail_after_registration(email, auth_token)
            return redirect('/token')

        except Exception as e:
            print(e)
    return render(request, 'register.html')

def success(request):
    return render(request, 'success.html')

def token_send(request):
    return render(request, 'token_send.html')

def verify(request, auth_token):
    try:
        profile_obj = Profile.objects.filter(auth_token=auth_token).first()
        if profile_obj:
            if profile_obj.is_verified:
                messages.success(request, 'Your account is already verified.')
                return redirect('/login')
            profile_obj.is_verified = True
            profile_obj.save()
            message.success(request, 'Your account has been verified.')
            return redirect('/login')
        else:
            return redirect('/error')
    except Exception as e:
        print(e)
    return redirect('/login')


def error(request):
    return render(request, 'error.html')

def send_mail_after_registration(email , token):
    subject = 'Your accounts need to be verified'
    message = f'Hi paste the link to verify your account http://127.0.0.1:8000/verify/{token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list)


def logout(request):
    auth.logout(request)
    return redirect('login_attempt')


# Reset password
# Sending email with token
def reset_pass_send_email(request):
    try:
        if request.method =='POST':
            email = request.POST.get('reset_password')
            user_obj = User.objects.filter(email=email).first()

            if user_obj is not None:
                profile_obj = Profile.objects.filter(user=user_obj.id).first()
                if (profile_obj.is_verified):
                    get_token = profile_obj.auth_token
                    send_mail_reset_password(email, get_token)
                    return redirect('/token')
    except Exception as e:
        print(e)
    return render(request, 'reset_pass_send_email.html')

def reset_password(request, get_token):
    context = {
        'get_token':get_token
    }
    return render(request, 'reset_password_form.html', context)



def reset_password_form(request, get_token):
    if request.method =='POST':
        password = request.POST['pass1']
        password2 = request.POST['pass2'] 
    
        profile_obj = Profile.objects.filter(auth_token = get_token).first()
        user_obj = User.objects.filter(username = profile_obj.user).first()
        if (password == password2):
            if user_obj:
                user_obj.set_password(password)
                user_obj.save()
                return redirect('/login')
        else:
            messages.success(request, 'Passwords are not matching.')
            return redirect(f'/reset_password/{get_token}')
    context = {
        'get_token':get_token
    }
    return render(request,'reset_password_form', context)



def send_mail_reset_password(email , get_token):
    subject = 'Reset Password'
    message = f'Follow this link to reset your password http://127.0.0.1:8000/reset_password/{get_token}'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message , email_from ,recipient_list)