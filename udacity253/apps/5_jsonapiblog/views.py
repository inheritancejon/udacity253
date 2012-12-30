from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from models import Post
import json
import re
import string
import hmac

# Define our regular expressions to be used
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r"^[\S]+@[\S]+\.[\S]+$")

# Generate json 
def generate_json(p):
    l = []
    # Try iterating over p
    try:
        for posts in p:
            l.append(dict({'subject':posts.subject,
                          'content':posts.content}))
           
        return json.dumps(l)
    # No good, probably single object
    except TypeError:
        d=dict({'subject':p.subject,
                'content':p.content})
        
        return json.dumps(d)
    return False
    
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

# Create blog entry submit form class
class SubmitForm(forms.Form):
    subject = forms.CharField()
    content = forms.CharField()

# Redirect to signup with blank user_id cookie    
def logout(request):
    response = redirect("jsonapiblog_signup")
    response.set_cookie("user_id", "", path="/")
    return response
   
## Return a simple HttpResponse with "Welcome, [username]"
def welcome(request):
    # If no cookie with key "user_id" is set, redirect to signup
    if not request.COOKIES.get("user_id"):
        return redirect("jsonapiblog_signup")
    # If cookie set, but not valid, redirect to signup
    if not check_secure_val(request.COOKIES.get("user_id")):
        return redirect("jsonapiblog_signup")
        
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
            request = redirect('jsonapiblog_welcome')
            # Set user_id cookie with encoded user pk id
            request.set_cookie('user_id', make_secure_val(str(m.pk)), path='/')
            # Return to welcome page
            return request
    else:
        form = LoginForm()
        username = ""
    
    #  Render template with username, form.errors
    d=dict(username=username, error=form.errors)
    return render_to_response('5_jsonapiblog/login.html', d, context_instance=RequestContext(request))

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
                response = redirect("jsonapiblog_welcome")
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
    return render_to_response("5_jsonapiblog/signup.html", d, context_instance=RequestContext(request))
    
# Display a blog post by its pk (primary key) id
def post(request, pk, json_api):
    # Was .json at the end of the URI?
    if json_api:
        post = get_object_or_404(Post, pk=int(pk))
        # Return a response with correct content-type and generated json
        return HttpResponse(generate_json(post), content_type="application/json")
    # Get post from Post model with pk passed from the URLconf, or throw 404
    post = get_object_or_404(Post, pk=int(pk))
    d=dict(post=post)
    return render_to_response("5_jsonapiblog/post.html", d, context_instance=RequestContext(request))

@csrf_exempt
def newpost(request):
    # Check if request is a POST, then process
    if request.method == 'POST':

        form = SubmitForm(request.POST)
        subject = form.data['subject']
        content = form.data['content']
        if form.is_valid():#
            # If form is valid, save new Post
            p = Post(subject=subject, content=content)
            p.save()
            # Redirect the browser to permae link ( p.pk = new post primary key)
            return HttpResponseRedirect("" + str(p.pk))
    else:
        # Request is not POST, leave the form blank
        form = SubmitForm()
        subject = ""
    
    # Render template with form data
    d=dict(subject=subject, error=form.errors)
    return render_to_response("5_jsonapiblog/newpost.html", d, context_instance=RequestContext(request))

# Return a response with blog posts passed to template
def index(request, json_api):
    # Was .json at the end of the URI?
    if json_api:
        posts = Post.objects.all().order_by("-date_created")[:10]
        # Return a response with correct content-type and generated json
        return HttpResponse(generate_json(posts), content_type="application/json")

    posts = Post.objects.all().order_by("-date_created")[:10]
    # Render home with list of entries
    d=dict(posts=posts)
    return render_to_response("5_jsonapiblog/index.html", d, context_instance=RequestContext(request))
