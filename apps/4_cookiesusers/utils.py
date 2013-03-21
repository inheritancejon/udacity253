from json import dumps
from datetime import datetime
from django.core.cache import cache
from django.contrib.auth.models import User
import hmac

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

def signed_in(request):
    if not request.COOKIES.get("user_id"):
        return False
    if not check_secure_val(request.COOKIES.get("user_id")):
        return False
    
    return User.objects.get(pk=int(check_secure_val(request.COOKIES.get("user_id"))))


