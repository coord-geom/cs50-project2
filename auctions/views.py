from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Category, Bid, Comment, Watchlist

class NewListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ['product_name', 'description', 'starting_bid', 'image', 'categories']
        widgets = {
            'product_name': forms.TextInput(attrs={'class': "form-control"}),
            'description':  forms.Textarea(attrs={'class': "form-control"}),
            'starting_bid': forms.NumberInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple,
            'image': forms.TextInput(attrs={'class': 'form-control'})
        }

        labels = {
            'product_name': 'Product Name',
            'starting_bid': 'Starting Bid (in dollars)',
            'image': 'Product Image URL (optional)',
            'categories': 'Categories (optional)'
        }

def index(request):
    pairs = []
    for listing in Listing.objects.exclude(active=False):
        bids = Bid.objects.filter(listing = listing)
        highest_bid = 0.00
        bid = None
        for bid_ in bids:
            if highest_bid < bid_.bid_price:
                highest_bid = bid_.bid_price
                bid = bid_
        if highest_bid == 0.00:
            pairs.append([listing, False])
        else:
            pairs.append([listing, highest_bid])
    return render(request, "auctions/index.html", {
        'pairs': pairs
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
            form.instance.seller = request.user
            form.save()
            return HttpResponseRedirect(reverse('listing', \
                kwargs={"ID": Listing.objects.latest('id').id}))
        else:
            return HttpResponseRedirect(reverse('create_listing'))

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
        Watchlist.objects.create(user=User.objects.get(username=username)).save()
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
            listing_ = Listing.objects.get(id=ID)
            bids = Bid.objects.filter(listing = listing_)
            highest_bid = 0.00
            bid = None
            for bid_ in bids:
                if highest_bid < bid_.bid_price:
                    highest_bid = bid_.bid_price
                    bid = bid_
            highest_bid = float(highest_bid)
            highest_bid += 0.01
            if request.user.is_authenticated:
                in_watchlist = (listing_ in Watchlist.objects.get(user=request.user).listings.all())
                return render(request, "auctions/listing.html", {
                    "listing": listing_,
                    "categories": listing_.categories.all(),
                    "bid": bid,
                    "bids": bids,
                    "user": request.user,
                    "min_bid": highest_bid,
                    "comments": Comment.objects.filter(listing=listing_),
                    "in_watchlist": in_watchlist
                })
            else:
                return render(request, "auctions/listing.html", {
                    "listing": listing_,
                    "categories": listing_.categories.all(),
                    "bid": bid,
                    "bids": bids,
                    "user": request.user,
                    "min_bid": highest_bid,
                    "comments": Comment.objects.filter(listing=listing_)
                })
        return HttpResponseRedirect(reverse('index'))
    elif request.method == "POST":
        listing_ = Listing.objects.get(id=ID)
        if 'place_bid' in request.POST:
            bid_price = request.POST["bid_price"]
            Bid.objects.create(
                bidder = request.user,
                bid_price = bid_price,
                listing = Listing.objects.get(id=ID)
            ).save()
        elif 'post_comment' in request.POST:
            message = request.POST["message"]
            Comment.objects.create(
                commenter = request.user,
                message = message,
                listing = Listing.objects.get(id=ID)
            ).save()
        elif 'add_to_watchlist' in request.POST:
            Watchlist.objects.get(user=request.user).listings.add(listing_)
        elif 'remove_from_watchlist' in request.POST:
            Watchlist.objects.get(user=request.user).listings.remove(listing_)
        elif 'close_auction' in request.POST:
            highest_bid = 0.00
            bid = None
            for bid_ in Bid.objects.filter(listing=listing_).all():
                if highest_bid < bid_.bid_price:
                    highest_bid = bid_.bid_price
                    bid = bid_
            listing_.active = False
            if not bid is None:
                listing_.winner = bid.bidder
            listing_.save()
        return HttpResponseRedirect(reverse('listing', kwargs={'ID': ID}))

def category(request, ID):
    if Category.objects.filter(id=ID).exists():
        category_ = Category.objects.get(id=ID)
        listings = []
        for listing in Listing.objects.exclude(active=False):
            if category_ in listing.categories.all():
                listings.append(listing)
        return render(request, 'auctions/category.html', {
            "listings": listings,
            "category": category_
        })
    else:
        return HttpResponseRedirect(reverse('categories'))
        
def watchlist(request):
    return render(request, 'auctions/watchlist.html', {
        'listings': Watchlist.objects.get(user=request.user).listings.all()
    })