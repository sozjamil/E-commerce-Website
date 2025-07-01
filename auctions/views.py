from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models import Max
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django import forms
from django.contrib import messages


from .models import *



class ListingForm(forms.ModelForm):
    # a Model form for Auction listing Model
    class Meta:
        model = AuctionListing
        fields = ['title', 'description',
                  'starting_bid', 'image', 'category'
                  ]

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class BidForm(forms.Form):
    getPrice = forms.DecimalField(max_digits=10, decimal_places=2, widget=forms.NumberInput(attrs={
            'class' : 'form-control',
            'placeholder': "Bid",
        }))
  
def index(request):
    # Authenticated users view their inbox
    if request.user.is_authenticated:
        active_listing=AuctionListing.objects.filter(active=True)
        return render(request, "auctions/index.html", {
            "listings": active_listing.order_by("-created_at").all(),
            "title": "Active Listing"
        })

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))


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

# @login_required    
def all_category(request):
    # users view all categories auctions containing closed auctions
    active_listing=AuctionListing.objects.all()
    categories=Category.objects.all()
    return render(request, "auctions/all_category.html", {
        "listings": active_listing.order_by("-created_at").all(),
        "categories": categories
    })


# @login_required
def show_category(request,category_id):
    # user can select a specific category to view this categories auctions 
    category=get_object_or_404(Category,id=category_id)
    listing=AuctionListing.objects.filter(active=True, category=category)
    all_categories=Category.objects.all()
    return render(request,"auctions/all_category.html", {
        "categories":all_categories,
        "listings":listing   
    })


@login_required
def create_listing(request):
    # user can create a new listing and should fill the form properly 
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.user = request.user
            listing.save()
            return redirect('single_listing', listing.id)
        else:
            print(form.errors)
    else:
        form = ListingForm()
    return render(request, "auctions/create.html", {
        "form": ListingForm()
    })


# @login_required
def single_listing(request, listing_id):
    # showing each listing with details 
    listing = AuctionListing.objects.get(pk=listing_id)
    isItInWatchlist = request.user in listing.watchlist.all()
    all_comment=Comments.objects.filter(auction=listing)
    max_price = listing.bids.all().aggregate(Max('bid_amount'))
    number_bids = listing.bids.all().count()
    
    return render(request, 'auctions/single_listing.html', {
        "listing": listing,
        "max_price": max_price,
        "getPrice": BidForm,
        "number_bids": number_bids,
        "isItInWatchlist": isItInWatchlist,
        "all_comment":all_comment
    })

@login_required
def watchlist(request):
    # users will be able to view their own watchlist auctions
    user = request.user
    listings = user.watchlist.all()
    return render(request, 'auctions/index.html', {
        'listings': listings,
        'title':"Your Watchlist"
    })

@login_required
def remove_watchlist(request, listing_id):
    # this function removes a specific item from the users watchlist 
    listing = AuctionListing.objects.get(pk=listing_id)
    user = request.user
    listing.watchlist.remove(user)
    return HttpResponseRedirect(reverse("single_listing", args=(listing.id, )))

@login_required
def add_watchlist(request, listing_id):
    #adds auction to the users watchlist 
    listing = AuctionListing.objects.get(pk=listing_id)
    user = request.user
    listing.watchlist.add(user)
    return HttpResponseRedirect(reverse("single_listing", args=(listing.id, )))


@login_required
def add_comment(request, listing_id):
    # users will be able to comment in any auction they want
    user=request.user
    listing=AuctionListing.objects.get(pk=listing_id)
    text=request.POST['new_comment']
    new_comment=Comments(
        user=user,
        auction=listing,
        text=text 
    )
    new_comment.save()
    return HttpResponseRedirect(reverse("single_listing", args=(listing.id, )))

def add_bid(request, listing_id):
    # users will be able to bid in any auction they want
    #the bid should be greater than the current bid
    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            price = form.cleaned_data['getPrice']
            item = AuctionListing.objects.get(id = listing_id)
            currentPrice = item.bids.all().aggregate(Max('bid_amount')).get('bid_amount__max', 0.00)
            print(currentPrice)
            if currentPrice == None and price <= item.starting_bid:
                messages.error(request, f'Price should greater than current price (${item.starting_bid})')
            elif currentPrice != None and price <= currentPrice:
                messages.error(request, f'Price should greater than current price (${currentPrice})')
            else:
                newBid = Bids(user = request.user, auction = item, bid_amount = price )
                newBid.save()
                messages.success(request, 'Done, Your Bid is the greatest Bid.')
    return redirect(reverse('single_listing', args=[listing_id]))

def close_listing(request, listing_id):
    # Auction owner can close the listing and the greatest bid will win the auction
    if request.method == 'POST':
        listing = AuctionListing.objects.get(id=listing_id)
        listing.active = False
        if listing.bids.count() != 0:
            listing.winner = listing.bids.first().user
        listing.save()
    return redirect(reverse('index'))

from django.db.models import Q

def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        results = AuctionListing.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query),
            active=True
        ).order_by('-created_at')
    categories = Category.objects.all()
    return render(request, "auctions/search.html", {
        "query": query,
        "results": results,
        "categories": categories
    })