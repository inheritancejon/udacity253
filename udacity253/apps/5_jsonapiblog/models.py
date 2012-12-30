from django.contrib import admin
from django.db import models

# The model for our blog entries
class Post(models.Model):
    subject = models.CharField(max_length=50)
    content = models.TextField()
    # Autofill the date_created field with current date
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Return subject as representation of object
    def __unicode__(self):
        return self.subject
    
