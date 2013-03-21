from django.db import models

# Create our user model
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    # Autofill the date_created field with current date
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Return username as representation of object
    def __unicode__(self):
        return self.username