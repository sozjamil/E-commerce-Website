from django.contrib import admin

# Register your models here.

from .models import User, AuctionListing, Bids, Comments, Category
    
admin.site.register(User)
admin.site.register(AuctionListing)
admin.site.register(Bids)
admin.site.register(Comments)
admin.site.register(Category)