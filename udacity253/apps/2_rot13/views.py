from django.shortcuts import render_to_response
from django.template import RequestContext
from django import forms
from django.views.decorators.csrf import csrf_exempt

# Create the Rot13 form class
class SubmitForm(forms.Form):
    text = forms.CharField()
    
# Encode ROT13
def rot13(s):
    if s:
        return s.encode("rot13")

# Return rendered template with form, and rot13 valid POST data 
@csrf_exempt
def index(request):

    rot13encoded = ""
    
    # Check if request is a POST, then process
    if request.method == 'POST':
        # Django automatically espaces form data
        form = SubmitForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            rot13encoded = rot13(cd['text'])
    else:
        # Request is not POST, leave 'text' blank
        form = SubmitForm()
    
    # Render template with encoded text passed along
    d=dict(text=rot13encoded)
    return render_to_response("2_rot13/index.html", d, context_instance=RequestContext(request))
