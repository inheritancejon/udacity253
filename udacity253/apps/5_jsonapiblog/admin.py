from django.contrib import admin
from models import Post

# Set admin page for blog entries to have a search field
# for "subject"
class PostAdmin(admin.ModelAdmin):
    search_fields = ["subject"]
    
# Register the model
admin.site.register(Post, PostAdmin)