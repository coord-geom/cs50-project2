from datetime import datetime
from decimal import Decimal
from django.contrib.auth.models import AbstractUser
from django.db import models

from django.core.validators import MinValueValidator

class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller')
    date = models.DateTimeField(default=datetime.now)
    product_name = models.CharField(max_length=128)
    description = models.TextField()
    starting_bid = models.DecimalField(decimal_places=2, max_digits=20, \
        validators=[MinValueValidator(Decimal('0.01'))])
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='categories')
    image = models.CharField(max_length=256, blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)

    def __str__(self):
        return f"{self.seller}'s {self.product_name}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(decimal_places=2, max_digits=20, \
        validators=[MinValueValidator(Decimal('0.01'))], default=0.01)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.bidder} bid {self.bid_price} for {self.listing}"



class Watchlist(models.Model):
    listings = models.ManyToManyField(Listing, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.user}'s watchlist"

class Comment(models.Model):
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    message = models.TextField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return f"{self.commenter} said on {self.listing}, \"{self.message}\""