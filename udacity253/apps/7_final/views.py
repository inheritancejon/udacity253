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

def return_wikipagehistory(i, v):
    try:
        j = WikiPageHistory.objects.filter(page=i).order_by('-version')[0]
        if v:
            try:
                j = WikiPageHistory.objects.get(page=i, version=v)
            except: return False
    except IndexError:
        j = WikiPageHistory.objects.get(page=i)

    return j

def index(request): 
    name = signed_in(request)
    heading = "List of wiki urls:"

    p = WikiPage.objects.all()
    if not p:
        heading = "There are no wiki urls. Log in and enter a url to create an entry."
   
    d=dict(pages=p, heading=heading, name=name)
    return render_to_response('7_final/index.html', d, context_instance=RequestContext(request))
        
def wiki(request, page):
    name = signed_in(request)
    v = request.GET.get('v')
    
    if page and WikiPage.objects.filter(page_url=page).exists():   
        i = WikiPage.objects.get(page_url=page)
        j = return_wikipagehistory(i, v)
        
        if not j:
            return redirect('7_final_wiki', page=page)

        d=dict(content=j.content, page=page, name=name, version=v, page_edit=True)
        return render_to_response('7_final/wiki.html', d, context_instance=(RequestContext(request)))
    else:
        return redirect('7_final__edit', page=page)

@csrf_exempt   
def _edit(request, page):

    name = signed_in(request)
    if not name: return redirect('7_final_index')

    if request.method == "POST":
        form = SubmitForm(request.POST)
        content = form.data['content']
        
        if form.is_valid():
            
            if not WikiPage.objects.filter(page_url=page).exists():
                m = WikiPage(page_url=page)
                m.save()
            else:
                m = WikiPage.objects.get(page_url=page)
             
            n = WikiPageHistory(page=m, content=content)
            n.save()

            return redirect('7_final_wiki', page=page)
    else:
        form = SubmitForm(request.POST)
        if WikiPage.objects.filter(page_url=page).exists():
            i = WikiPage.objects.get(page_url=page)
            j = return_wikipagehistory(i, request.GET.get('v'))
            if not j:
                return redirect('7_final__edit', page=page)
            content = j.content
        else:
            content = ""

    d=dict(content=content, page=page, name=name)
    return render_to_response("7_final/edit.html", d, context_instance=RequestContext(request))

def _history(request, page):

    name = signed_in(request)
    if not name: return redirect('7_final_index')

    v = ''

    if WikiPage.objects.filter(page_url=page).exists():
        i = WikiPage.objects.get(page_url=page)
        try:
            v = WikiPageHistory.objects.filter(page=i).order_by('-version')
        except IndexError:
            v = WikiPageHistory.objects.get(page=i)
    
    
    d=dict(versions=v, page=page, name=name)
    return render_to_response('7_final/history.html', d, context_instance=RequestContext(request))

###
# Redirect to signup with blank user_id cookie    
def logout(request):
    response = redirect("7_final_index")
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
            request = redirect('7_final_wiki')
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
                response = redirect("7_final_wiki")
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
    