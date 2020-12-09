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
    description = models.TextField(default='Give a short description of your product.')
    starting_bid = models.DecimalField(decimal_places=2, max_digits=20, \
        validators=[MinValueValidator(Decimal('0.01'))])
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='categories')
    image = models.ImageField(upload_to='', blank=True, null=True)
    winner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='winner', blank=True, null=True)

    def __str__(self):
        return f"{self.product_name} by {self.seller}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    bid_price = models.DecimalField(decimal_places=2, max_digits=20, \
        validators=[MinValueValidator(Decimal('0.01'))], default=0.01)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)

class Watchlist(models.Model):
    listings = models.ForeignKey(Listing, on_delete=models.CASCADE, blank=True, null=True)
