from django.contrib import admin
from django.db import models
from datetime import datetime

# The model for our blog entries
class WikiPage(models.Model):
    page_url = models.CharField(max_length=128)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # Return subject as representation of object
    def __unicode__(self):
        return self.page_url
    
class WikiPageHistory(models.Model):
    page = models.ForeignKey('WikiPage')
    version = models.IntegerField()
    content = models.TextField()
    date_created = models.DateTimeField()
    
    # Return subject as representation of object
    def __unicode__(self):
        return "Page_url:" + self.page.page_url + " Version: " + str(self.version)
    
    def save(self):
        try:
            top = WikiPageHistory.objects.filter(page=self.page).order_by('-version')[0]
            self.version = top.version + 1
        except IndexError:
            self.version = 1

        self.date_created = datetime.now()
        
        super(WikiPageHistory, self).save()
        
