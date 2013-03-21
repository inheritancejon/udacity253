import re
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

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

# Create the user signup form 
class SubmitForm(forms.Form):
    # Define form fields
    # - 'required' is set to false to prevent automatic 
    #    raise of validation error; clean functions catch
    #    invalid matches (including empty fields)
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
        # Always return scrubbed data
        return username
    
    # Validate email
    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        # Only raise error if email field is invalid AND not empty
        if (email != "") and not validate(email, EMAIL_RE):
            raise forms.ValidationError("Invalid Email")
 
        return email
    
    # Validate password and verify
    # - This is done in a parent clean because the error message 
    #   that is reported depends on these two fields being linked, I.E.:
    #   -  If password is invalid, always display invalid password
    #      but not password mismatch.
    #   -  If password is valid, but there is a mismatch, THEN show
    #      mismatch error.
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
   
# Return a simple HttpResponse with "Welcome, [username]"
def welcome(request):
    name = request.GET['username']
    message = "Welcome, " + name
    return HttpResponse(message)

# - Django by default requires csrf tokens used on forms to prevent 
#   foreign site forgeries. csrf_exempt decorator is used so Udacity
#   can validate POST. 
# Return either a rendered template with the user singup form, or
# redirect to the welcome message.
@csrf_exempt
def index(request):
    
    # Check if request is a POST, then process
    if request.method == 'POST':
        # Request is POST, validate input
        # Django automatically espaces form data
        form = SubmitForm(request.POST)
        # Get username and email field so form is repopulated
        username = form.data['username']
        email = form.data['email']
        if form.is_valid():
            #Success message, redirect to new view with GET data 
            return redirect("welcome/?username=" + username)
    else:
        # Request is not POST, leave the form blank
        form = SubmitForm()
        username = ""
        email = ""
    
    # Render template with form data
    # Never repopulate password or verify field, but pass errors
    d=dict(username=username, email=email, error=form.errors)
    return render_to_response("2_usersignup/index.html", d, context_instance=RequestContext(request))
