import re
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
import string
import random
import hmac
from utils import signed_in

# Define our regular expressions to be used
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

# Validate strings matching regular expressions
def validate(s, reg):
    if s:
        if reg.match(s):
            return True
        else:
            return False

# secret key for salt    
secret = "pooohateojaspdiofj02983ufsdfji"

# Create secure cookie value
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

# Check if is value is checks out
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val

class LoginForm(forms.Form):
    username = forms.CharField(required=False)
    password = forms.CharField(required=False)
    
    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        
        if not validate(username, USER_RE):
            raise forms.ValidationError("Invalid Username")
        
        if not User.objects.filter(username=username).count():
            raise forms.ValidationError("User does not exists")
        
        return username
    
    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        
        if not validate(password, PASSWORD_RE):
            raise forms.ValidationError("Password Invalid")
        
        return password
    
    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        
        if User.objects.filter(username=username).count():
            m = User.objects.get(username=username)
            if not m.check_password(password):
                self._errors['username'] = "Username/Password Don't Match"
            
        return username, password

# Create the user signup form 
class RegisterForm(forms.Form):
    # Define form fields
    username = forms.CharField(required=False)
    password = forms.CharField(required=False)
    verify = forms.CharField(required=False)
    email = forms.CharField(required=False)
    
    # Validate username
    def clean_username(self):
        # Get username data
        username = self.cleaned_data.get('username', None)
        # If not validated by regular expression, raise error
        if not validate(username, USER_RE):
            raise forms.ValidationError("Invalid Username")      
        # If user already exists, raise error
        if User.objects.filter(username=username).count():
            raise forms.ValidationError("Username Already Exists")
        
        return username
    
    # Validate email
    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        # Only raise error if email field is invalid AND not empty
        if (email != "") and not validate(email, EMAIL_RE):
            raise forms.ValidationError("Invalid Email")
 
        return email
    
    # Validate password and verify
    def clean(self):
        password = self.cleaned_data.get('password', None)
        verify = self.cleaned_data.get('verify', None)
        # If not validated by regular expression, raise error
        if not validate(password, PASSWORD_RE):
            self._errors["password"] = self.error_class(['Invalid Password'])
        
            return verify, password
        
        # If password valid, check for password mismatch, raise error
        if verify != password:
            self._errors["verify"] = self.error_class(["Passwords do not match"])
        
        return verify, password
@csrf_exempt
def logout(request):
    response = redirect("cookiesusers_signup")
    response.set_cookie("user_id", "", path="/")
    return response
   
# Return a simple HttpResponse with "Welcome, [username]"
@csrf_exempt
def welcome(request):
    # If no cookie with key "user_id" is set, redirect to signup
    if not request.COOKIES.get("user_id"):
        return redirect("cookiesusers_signup")
    # If cookie set, but not valid, redirect to signup
    if not check_secure_val(request.COOKIES.get("user_id")):
        return redirect("cookiesusers_signup")
        
    # Get user from the ID in the cookie (User returns unicode username as represenation of object)
    name = User.objects.get(pk=int(check_secure_val(request.COOKIES.get("user_id"))))
    
    # Return welcome message
    return HttpResponse("Welcome, %s!" % name)

@csrf_exempt
def login(request):
    # Check if user is signed in (check cookie)
    name = signed_in(request)

    users = User.objects.all()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = form.data['username']
        
        if form.is_valid():
            m = User.objects.get(username=username)
            request = redirect('cookiesusers_welcome')

            request.set_cookie('user_id', make_secure_val(str(m.pk)), path='/')
            return request
        
    else:
        form = LoginForm()
        username = ""
        
    d=dict(username=username, error=form.errors, name=name)
    return render_to_response('4_cookiesusers/login.html', d, context_instance=RequestContext(request))
# Return either a rendered template with the user singup form, or
# redirect to the welcome message.
@csrf_exempt
def signup(request):
    # Check if user is signed in (check cookie)
    name = signed_in(request)

    users = User.objects.all()
    # Check if request is a POST, then process
    if request.method == 'POST':
        # Request is POST, validate input
        # Django automatically espaces form data
        form = RegisterForm(request.POST)
        # Get username and email field so form is repopulated
        username = form.data['username']
        email = form.data['email']
        password = form.data['password']
        
        if form.is_valid():
            try: 
                # Create a new User object
                m = User.objects.create_user(username=username,
                                             email=email,
                                             password=password)
                # Save the object
                m.save()
                # Create the response
                response = redirect("cookiesusers_welcome")
                # Set the cookie
                response.set_cookie("user_id", make_secure_val(str(m.pk)), path="/")
                # Return redirect/set-cookie
                return response
            except User.DoesNotExist:
                # Fail safe; user check occurs in clean_user
                raise Http404()
    else:
        # Request is not POST, leave the form blank
        form = RegisterForm()
        username = ""
        email = ""
    
    # Render template with form data
    # Never repopulate password or verify field, but pass errors
    d=dict(username=username, email=email, error=form.errors, name=name)
    return render_to_response("4_cookiesusers/signup.html", d, context_instance=RequestContext(request))
