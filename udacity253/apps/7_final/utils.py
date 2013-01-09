"""
A useful collection of tools from throughout
the entire course
"""
from json import dumps
from datetime import datetime
from django.core.cache import cache
from django.contrib.auth.models import User
import hmac

# secret key for salt    
secret = "pooohateojaspdiofj02983ufsdfji"

# Validate strings matching regular expressions
def validate(s, reg):
    if s:
        if reg.match(s):
            return True
        else:
            return False 
        
# Create secure cookie value
def make_secure_val(val):
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())

# Check if is value is checks out
def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val
    
# Generate json 
def generate_json(p):
    l = []
    # Try iterating over p
    try:
        for posts in p:
            l.append(dict({'subject':posts.subject,
                          'content':posts.content}))
           
        return dumps(l)
    # No good, probably single object
    except TypeError:
        d=dict({'subject':p.subject,
                'content':p.content})
        
        return dumps(d)
    return False

# Update a cache key with timestamp
def update_cache(key, value):
    now = datetime.utcnow()
    cache.set(key, (value, now), 60 * 10)

# Return total seconds from now
def calculate_age_in_seconds(age):
    return (datetime.utcnow() - age).total_seconds()

# Check for valid user_id cookie, return username or False
def signed_in(request):
    if not request.COOKIES.get("user_id"):
        return False
    if not check_secure_val(request.COOKIES.get("user_id")):
        return False
    
    return User.objects.get(pk=int(check_secure_val(request.COOKIES.get("user_id"))))


