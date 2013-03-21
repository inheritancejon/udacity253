from django.contrib import admin
from models import User

# Set admin page for blog entries to have a search field
# for "subject"
class UserAdmin(admin.ModelAdmin):
    search_fields = ["subject"]
    
# Register the model
admin.site.register(User, UserAdmin)