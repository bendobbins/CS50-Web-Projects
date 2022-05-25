from django.contrib import admin
from .models import Item, User, Comment, Listing, Bid, Watchlist

# Register your models here.
admin.site.register(Item)
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Listing)
admin.site.register(Bid)
admin.site.register(Watchlist)