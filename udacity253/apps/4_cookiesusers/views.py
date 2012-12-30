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

# Create the user login form class
class LoginForm(forms.Form):
    username = forms.CharField(required=False)
    password = forms.CharField(required=False)
    
    # Validate username
    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        # If not validated by regular expression, raise error
        if not validate(username, USER_RE):
            raise forms.ValidationError("Invalid Username")
        # If username already exists, raise error
        if not User.objects.filter(username=username).count():
            raise forms.ValidationError("User does not exists")
        
        return username
    
    # Validate password
    def clean_password(self):
        password = self.cleaned_data.get('password', None)
        # If not validated by regular expression, raise error
        if not validate(password, PASSWORD_RE):
            raise forms.ValidationError("Password Invalid")
        
        return password
    
    # Validate password/username match
    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)
        # If username exists but username doesn't match password, raise error
        if User.objects.filter(username=username).count():
            m = User.objects.get(username=username)
            if not m.check_password(password):
                self._errors['username'] = "Username/Password Don't Match"
            
        return username, password

# Create the user register form class
class RegisterForm(forms.Form):
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
    
# Redirect to signup with blank user_id cookie    
def logout(request):
    response = redirect("cookiesusers_signup")
    response.set_cookie("user_id", "", path="/")
    return response
   
# Return a simple HttpResponse with "Welcome, [username]"
def welcome(request):
    # If no cookie with key "user_id" is set, redirect to signup
    if not request.COOKIES.get("user_id"):
        return redirect("cookiesusers_signup")
    # If cookie set, but not valid, redirect to signup
    if not check_secure_val(request.COOKIES.get("user_id")):
        return redirect("cookiesusers_signup")
        
    # Get user from the ID in the cookie (User returns unicode username as represenation of object)
    name = User.objects.get(pk=int(check_secure_val(request.COOKIES.get("user_id"))))

    return HttpResponse("Welcome, %s!" % name)

# Return either a rendered template with the user login form, or
# redirect to the welcome message
@csrf_exempt
def login(request):
    users = User.objects.all()
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = form.data['username']
        
        if form.is_valid():
            # User name exists (checked in form clean_username), get user
            m = User.objects.get(username=username)
            request = redirect('cookiesusers_welcome')
            # Set user_id cookie with encoded user pk id
            request.set_cookie('user_id', make_secure_val(str(m.pk)), path='/')
            # Return to welcome page
            return request
    else:
        form = LoginForm()
        username = ""
    
    #  Render template with username, form.errors
    d=dict(username=username, error=form.errors)
    return render_to_response('4_cookiesusers/login.html', d, context_instance=RequestContext(request))

# Return either a rendered template with the user singup form, or
# redirect to the welcome message.
@csrf_exempt
def signup(request):
    users = User.objects.all()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
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
    
    # Render template with username, email, form.errors
    # Never repopulate password or verify field, but pass errors
    d=dict(username=username, email=email, error=form.errors)
    return render_to_response("4_cookiesusers/signup.html", d, context_instance=RequestContext(request))
