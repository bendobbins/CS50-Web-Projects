from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Item(models.Model):
    name = models.CharField(max_length=64)
    price = models.IntegerField()
    image = models.CharField(max_length=1000)
    description = models.CharField(max_length=700)
    category = models.CharField(max_length=64)

class Listing(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name="itemListings")
    lister = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    datetime = models.DateTimeField()
    closed = models.BooleanField(default=False)

class Comment(models.Model):
    comment = models.CharField(max_length=1500)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingComments")
    datetime = models.DateTimeField()

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingBids")
    leader = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="biddingLeaders")
    numbids = models.IntegerField()

class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usersWatching")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listingsWatched")