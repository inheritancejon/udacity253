from django.http import HttpResponse, HttpResponseRedirect
from django import forms
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from models import Post

# Create blog entry submit form class
class SubmitForm(forms.Form):
    subject = forms.CharField()
    content = forms.CharField()
    
# Display a blog post by its pk (primary key) id
def post(request, pk):
    # Get post from Post model with pk passed from the URLconf, or throw 404
    post = get_object_or_404(Post, pk=int(pk))
    d=dict(post=post)
    # Render post with blog entry
    return render_to_response("3_basicblog/post.html", d, context_instance=RequestContext(request))

# Redirect to permalink if POST is is valid and blog saved, otherwise re-render with form/errors
@csrf_exempt
def newpost(request):
    
    # Check if request is a POST, then process
    if request.method == 'POST':
        # Request is POST, validate input
        # Django automatically espaces form data
        # Get subject so the form is re-populated
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
    return render_to_response("3_basicblog/newpost.html", d, context_instance=RequestContext(request))

# Return a response with blog posts passed to template
def index(request):
    # Grab a list of last ten posts ordered by most recently created
    posts = Post.objects.all().order_by("-date_created")[:10]
    posts = list(posts)
    # Render index with list of blog entries
    d=dict(posts=posts)
    return render_to_response("3_basicblog/index.html", d, context_instance=RequestContext(request))