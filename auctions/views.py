from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from decimal import Decimal

from .models import User, Listing, Category, Bid

class NewListingForm(forms.Form):
    product_name = forms.CharField(max_length=256, label="Product Name", \
        widget=forms.TextInput(attrs={'class': "form-control"}))
    description = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))
    starting_bid = forms.DecimalField(label="Starting Bid (in dollars)", \
        max_digits=20, decimal_places=2, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    product_image = forms.ImageField(required=False, label="Product Image (optional)")
    categories = forms.ModelMultipleChoiceField(
                    widget = forms.CheckboxSelectMultiple,
                    queryset = Category.objects.all()
                )


def index(request):
    return render(request, "auctions/index.html", {
        'listings': Listing.objects.exclude(active=False)
    })

def categories(request):
    return render(request, "auctions/categories.html", {
        "categories": Category.objects.all()
    })

@login_required(login_url='login')
def create_listing(request):
    if request.method == "GET":
        return render(request, "auctions/create_listing.html", {
            "form": NewListingForm()
        })
    elif request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            product_name = form.cleaned_data["product_name"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            product_image = form.cleaned_data["product_image"]
            obj = Listing.objects.create(
                seller = request.user,
                product_name = product_name,
                description = description,
                starting_bid = starting_bid,
                image = product_image,
            )
            obj.categories.set(form.cleaned_data["categories"])
            obj.save()
            return HttpResponseRedirect(reverse('listing', \
                kwargs={"ID": Listing.objects.latest('id').id}))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required(login_url='login')
def my_listings(request):
    return render(request, "auctions/mylistings.html", {
        "listings": Listing.objects.filter(seller=request.user)
    })

def listings(request, ID):
    if request.method == "GET":
        if Listing.objects.filter(id=ID).exists():
            found_listing = Listing.objects.get(id=ID)
            bids = Bid.objects.filter(listing = found_listing)
            highest_bid = 0.00
            bid = None
            for bid_ in bids:
                if highest_bid < bid_.bid_price:
                    highest_bid = bid_.bid_price
                    bid = bid_
            highest_bid += Decimal(0.01)
            return render(request, "auctions/listing.html", {
                "listing": found_listing,
                "categories": found_listing.categories.all(),
                "bid": bid,
                "bids": bids,
                "user": request.user,
                "min_bid": highest_bid
            })
        return HttpResponseRedirect(reverse('index'))
    elif request.method == "POST":
        bid_price = request.POST["bid_price"]
        obj = Bid.objects.create(
            bidder = request.user,
            bid_price = bid_price,
            listing = Listing.objects.get(id=ID)
        )
        obj.save()
        found_listing = Listing.objects.get(id=ID)
        bids = Bid.objects.filter(listing = found_listing)
        highest_bid = 0.00
        bid = None
        for bid_ in bids:
            if highest_bid < bid_.bid_price:
                highest_bid = bid_.bid_price
                bid = bid_
        highest_bid += Decimal(0.01)
        return render(request, "auctions/listing.html", {
            "listing": found_listing,
            "categories": found_listing.categories.all(),
            "bid": bid,
            "bids": bids,
            "user": request.user,
            "min_bid": highest_bid
        })
        
