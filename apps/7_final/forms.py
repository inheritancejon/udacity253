from django import forms
from django.contrib.auth.models import User
from re import compile

#Define our regular expressions to be used
USER_RE = compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = compile(r"^.{3,20}$")
EMAIL_RE = compile(r"^[\S]+@[\S]+\.[\S]+$")

# Validate strings matching regular expressions
def validate(s, reg):
    if s:
        if reg.match(s):
            return True
        else:
            return False

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
    content = forms.CharField()
