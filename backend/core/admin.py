from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

admin.site.register(User, UserAdmin)
admin.site.register(WishList)
admin.site.register(WishListItem) 
admin.site.register(Notification)