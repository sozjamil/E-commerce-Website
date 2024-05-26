from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

class AuctionListing(models.Model):
    title = models.CharField(max_length=64, null=False)
    description = models.TextField(max_length=256)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=1, null=False)
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    active  = models.BooleanField(default=True)
    watchlist = models.ManyToManyField(User, blank=True, related_name="watchlist")
    winner=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="winner")
    
    def __str__(self):
        return self.title

class Bids(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bid_amount= models.DecimalField(max_digits=5, decimal_places=1)

    def __str__(self):
        return str(self.bid_amount)

class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    auction = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    text = models.CharField(max_length=256)
    created_at= models.DateTimeField(auto_now_add=True)
    
    def  __str__(self):
        return  f"{self.user } comment on { self.auction}"

