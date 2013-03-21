# Make this unique, and don't share it with anybody. Define your secret key in 
# secret_key.py in this files path 
# https://docs.djangoproject.com/en/1.5/topics/signing/

MODE = "development"

if MODE == "production":
    from settings_development import *
else:
    from settings_production import *  

