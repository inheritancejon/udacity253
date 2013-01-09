from django.contrib import admin
from models import WikiPage, WikiPageHistory

# Register the models for easy management

admin.site.register(WikiPage)
admin.site.register(WikiPageHistory)
