from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.template import RequestContext
from django.utils.functional import wraps
from models import WikiPage, WikiPageHistory
from forms import *
from utils import signed_in, check_secure_val, make_secure_val

# Get a pages history of edits
def return_wikipagehistory(i, v):
    # Try getting a url's edit history via WikiPage object
    try:
        j = WikiPageHistory.objects.filter(page=i).order_by('-version')[0]
        # If a version number (whole numbers (1,2,5,255,etc..) filter entry by version #
        if v:
            try:
                j = WikiPageHistory.objects.get(page=i, version=v)
            # Return no previous version/version of that #
            except: return False
    # Everything sucked, just grab the base page we hope
    except IndexError:
        j = WikiPageHistory.objects.get(page=i)
    
    return j

# Generally page request
def wiki(request, page):
    # Check if user is signed in
    name = signed_in(request)
    
    # Have to do special stuff with handling the app home URN index
    if request.path.endswith("/"):
        page = "index"
    
    # Are we looking at an older version, from url '?v=(version_number)'
    v = request.GET.get('v')
    
    # So our url is a valid existing wiki entry...
    if page and WikiPage.objects.filter(page_url=page).exists():
        # i = grab page, j = grab history (if it exists)
        i = WikiPage.objects.get(page_url=page)
        j = return_wikipagehistory(i, v)
        # page not there? just go (to the) home (url for this app)        
        if not j:
            if page == "index": page = ''
            return redirect('final_wiki', page=page)

        # Regular pass along to template
        d=dict(content=j.content, page=page, name=name, version=v)
        return render_to_response('7_final/index.html', d, context_instance=(RequestContext(request)))
    else:
        # Page exists, but there is no other versions, so time to create new versions!        
        return redirect('final__edit', page=page)

# Edit whatever wiki page you are on
@csrf_exempt   
def _edit(request, page):
    # Have to do special stuff with handling the app home URN index
    if page == None:
        page = 'index'

    # Check if user is signed in, if not, go back to the app index       
    name = signed_in(request)
    if not name: return redirect('final_wiki', page='')

    # Is this post?
    if request.method == "POST":
        # Grab post info
        form = SubmitForm(request.POST)
        content = form.data['content']
        
        if form.is_valid():
            # If this wikipage doesn't exist, create new and save
            if not WikiPage.objects.filter(page_url=page).exists():
                m = WikiPage(page_url=page)
                m.save()
            
            # If it does, grab it so we can update this page's history
            else:
                m = WikiPage.objects.get(page_url=page)
            
            # Update this pages wikihistory!
            n = WikiPageHistory(page=m, content=content)
            n.save()
            
            # Redirect back to the new page (handle index URN)
            if page == 'index':
                page = ''
            return redirect('final_wiki', page=page)

    # No post, so present the form to edit a wikipage
    else:
        # Create wikipage form
        form = SubmitForm(request.POST)

        # Show the values for the current page in the wikipage form        
        if WikiPage.objects.filter(page_url=page).exists():
            i = WikiPage.objects.get(page_url=page)
            j = return_wikipagehistory(i, request.GET.get('v'))
            
            # If there is no page history, make sure the index (/) is referred to as (index)         
            if not j:
                if page == "index":
                    page = ''             
                return redirect('final__edit', page=page)
            
            # Where we pass the form content to the _edit view          
            content = j.content
        else:
            # Just pass blank content to the form, this is a new page
            content = ""
    
    # Pass along stuff and render 
    d=dict(content=content, page=page, name=name)
    return render_to_response("7_final/edit.html", d, context_instance=RequestContext(request))

# View the history of a wikipage
def _history(request, page):
    # Handle index (/) page naming
    if page == None: page = 'index'
    
    # Check if user is signed in
    name = signed_in(request)
    if not name: return redirect('final_wiki', page='')
    
    # blank version #
    v = ''

    # More than one version of this page exist?
    if WikiPage.objects.filter(page_url=page).exists():
        i = WikiPage.objects.get(page_url=page)
        try:
            v = WikiPageHistory.objects.filter(page=i).order_by('-version')
        # Only one version exists        
        except IndexError:
            v = WikiPageHistory.objects.get(page=i)
    
    # Pass along stuff and render 
    d=dict(versions=v, page=page, name=name)
    return render_to_response('7_final/history.html', d, context_instance=RequestContext(request))

###
# Redirect to signup with blank user_id cookie    
def logout(request):
    response = redirect("final_wiki")
    response.set_cookie("user_id", "", path="/")
    return response

# Return either a rendered template with the user login form, or
# redirect to the welcome message
@csrf_exempt
def login(request):

    if request.method == 'POST':
        form = LoginForm(request.POST)
        username = form.data['username']
        
        if form.is_valid():
            m = User.objects.get(username=username)
            request = redirect('final_wiki')
            # Set user_id cookie with encoded user pk id
            request.set_cookie('user_id', make_secure_val(str(m.pk)), path='/')
            return request
    else:
        form = LoginForm()
        username = ""
    
    #  Render template with username, form.errors
    d=dict(username=username, error=form.errors)
    return render_to_response('7_final/login.html', d, context_instance=RequestContext(request))

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
                response = redirect("final_wiki")
                # Set the cookie
                response.set_cookie("user_id", make_secure_val(str(m.pk)), path="/")
                return response
    else:
        form = RegisterForm()
        username = ""
        email = ""

    # Render template with username, email, form.errors
    d=dict(username=username, email=email, error=form.errors)
    return render_to_response("7_final/signup.html", d, context_instance=RequestContext(request))
    
