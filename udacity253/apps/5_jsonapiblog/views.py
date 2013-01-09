from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.template import RequestContext
from models import Post
from django.db import connections, transaction

from utils import *
from forms import *

# Redirect to signup with blank user_id cookie    
def logout(request):
    response = redirect("jsonapiblog_signup")
    response.set_cookie("user_id", "", path="/")
    return response
   
# Return a simple HttpResponse with "Welcome, [username]"
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

    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = form.data['username']
        
        if form.is_valid():
            m = User.objects.get(username=username)
            request = redirect('jsonapiblog_welcome')
            # Set user_id cookie with encoded user pk id
            request.set_cookie('user_id', make_secure_val(str(m.pk)), path='/')
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

    if request.method == 'POST':
    
        form = RegisterForm(request.POST)
        username = form.data['username']
        email = form.data['email']
        password = form.data['password']
        
        if form.is_valid(): 
            # Create a new User object
            if User.objects.filter(username=username).count():
                form._errors['username'] = form.error_class(["Username Already Exists"])
            else:
                m = User.objects.create_user(username=username,
                                             email=email,
                                             password=password)
                m.save()
                response = redirect("jsonapiblog_welcome")
                # Set the cookie
                response.set_cookie("user_id", make_secure_val(str(m.pk)), path="/")
                return response
    else:
        form = RegisterForm()
        username = ""
        email = ""

    # Render template with username, email, form.errors
    d=dict(username=username, email=email, error=form.errors)
    return render_to_response("5_jsonapiblog/signup.html", d, context_instance=RequestContext(request))
    
# Display a blog post by its pk (primary key) id
def post(request, pk, json_api):

    if cache.get('POST_ID_' + str(pk)) == None:
        post = get_object_or_404(Post, pk=int(pk))
        update_cache('POST_ID_'+ str(pk), post)
        age = 0
    else:
        post, age = cache.get('POST_ID_' + str(pk))
        age = calculate_age_in_seconds(age)
    
    # Was .json at the end of the URI?
    if json_api:
        return HttpResponse(generate_json(post), content_type="application/json")
    
    # Get post from Post model with pk passed from the URLconf, or throw 404
    post = get_object_or_404(Post, pk=int(pk))
    d=dict(post=post, age=age)
    return render_to_response("5_jsonapiblog/post.html", d, context_instance=RequestContext(request))

@csrf_exempt
def newpost(request):

    if request.method == 'POST':

        form = SubmitForm(request.POST)
        subject = form.data['subject']
        content = form.data['content']
        if form.is_valid():#
            # If form is valid, save new Post
            p = Post(subject=subject, content=content)
            p.save()
            # Redirect the browser to permae link ( p.pk = new post primary key)
            update_cache('POST_ID_' + str(p.pk), p)
            return HttpResponseRedirect("" + str(p.pk))
    else:
        # Request is not POST, leave the form blank
        form = SubmitForm()
        subject = ""
    
    # Render template with form data
    d=dict(subject=subject, error=form.errors)
    return render_to_response("5_jsonapiblog/newpost.html", d, context_instance=RequestContext(request))

# Flush the cache
def flush(request):
    # Clear cache
    cache.clear()
    # Workaround for db cache with sqlite
    cursor = connections['default'].cursor()
    cursor.execute('DELETE FROM my_cache_table')
    transaction.commit_unless_managed(using='default')
    return redirect("jsonapiblog_index")

# Return a response with blog posts passed to template
#@cache_page
def index(request, json_api):
    age = 0
    if cache.get('POSTS') == None:
        posts = Post.objects.all().order_by("-date_created")[:10]
        update_cache('POSTS', posts)
    else:
        posts, age = cache.get('POSTS')
        age = calculate_age_in_seconds(age)

    # Was .json at the end of the URI?
    if json_api:
        # Return a response with correct content-type and generated json
        return HttpResponse(generate_json(posts), content_type="application/json")

    # Render home with list of entries
    d=dict(posts=posts, age=age)
    return render_to_response("5_jsonapiblog/index.html", d, context_instance=RequestContext(request))
