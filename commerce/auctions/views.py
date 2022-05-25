from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import User, Item, Comment, Bid, Listing, Watchlist


def index(request):
    # Render all listings that have not been closed
    return render(request, "auctions/index.html", {
        "title": "Auctions",
        "listings": Listing.objects.exclude(closed=True)
    })


@login_required
def watchlist(request):
    # POST to watchlist comes from listings page, update watchlist and redirect back to same listings page
    if request.method == "POST":
        listID = request.POST["listing"]
        listing = Listing.objects.get(pk=listID)

        if request.POST["watchlist"] == "add":
            Watchlist(user=User.objects.get(username=request.user), listing=listing).save()
        else:
            Watchlist.objects.filter(user=User.objects.get(username=request.user), listing=listing).delete()

        return HttpResponseRedirect(f"listing/{listID}")     # Redirect back to listing page they were on (not sure how to use reverse with the listID)

    # GET for watchlist goes to watchlist route, displays all listings in user watchlist
    watchings = Watchlist.objects.filter(user=User.objects.get(username=request.user))
    listings = []
    for watching in watchings:                  # Create a list of the listings the user is watching
        listings.append(watching.listing)

    return render(request, "auctions/index.html", {
        "title": "Watchlist",
        "listings": listings,
        "watchlist": True
    })


def categories(request):
    # POST is user selecting category to see listings for, return index template with listings for that category
    if request.method == "POST":
        category = request.POST["category"]
        openListings = Listing.objects.filter(closed=False)     # Get all listings that are not closed

        listings = []
        for listing in openListings:                            # Create a list of open listings that correspond to the category
            if listing.item.category == category:
                listings.append(listing)

        return render(request, "auctions/index.html", {
            "title": f"Listings for {category}",
            "listings": listings,
            "category": category
        })

    # GET should display radio list of selections for user where each selection is a category that has item listings
    items = Item.objects.all()
    categories = set()
    for item in items:                  # Create a set of all categories used for items on the site
        if item.category:
            categories.add(item.category)

    return render(request, "auctions/categories.html", {
        "title": "Categories",
        "categories": categories
    })


@login_required
def create(request):
    # POST should create a new listing and bid if the created submission is valid, then redirect back to home page
    if request.method == "POST":
        title = request.POST["title"]
        try:
            price = int(request.POST["price"])          # If title or price are invalid, do not create submission
        except ValueError:
            title = None

        if title:
            image = request.POST["image"]
            category = request.POST["category"]
            description = request.POST["description"]
            item = Item(name=title.lower().capitalize(), price=price, image=image, category=category.lower().capitalize(), description=description)         # Create new item with all information
            item.save()

            user = User.objects.get(username=request.user)
            time = datetime.datetime.now()
            listing = Listing(item=item, lister=user, datetime=time)            # Create new listing with item, user and datetime (closed is false by default)
            listing.save()

            Bid(listing=listing, numbids=0).save()                          # Create new bid for listing (each listing should have no more and no less than 1 bid)

        return HttpResponseRedirect(reverse("index"))

    # Render creation template if GET
    return render(request, "auctions/create.html")


def listing(request, id):
    # Should return a page displaying all information for a listing, and allow bidding, closing and watchlisting of item if valid
    listing = Listing.objects.get(pk=id)
    bids = listing.listingBids.all()

    try:
        watching = Watchlist.objects.filter(user=User.objects.get(username=request.user), listing=listing)
        watchlist = True if watching else False                     # Find if item is on user watchlist
    except User.DoesNotExist:
        watchlist = None

    # bids should be a list of 1 Bid since there should only be 1 Bid per listing
    # bid will then represent that Bid
    for b in bids:
        bid = b

    if request.method == "POST":                        # POST requests are for comments, still should render listing page as normal
        comment = request.POST["comment"]
        if comment:
            time = datetime.datetime.now()
            Comment(comment=comment, commenter=User.objects.get(username=request.user), listing=listing, datetime=time).save()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": listing.listingComments.all(),
        "bid": bid,
        "leading": True if bid.leader and bid.leader.username == request.user.username else False,          # If user is leading bidding, this is true
        "creator": True if request.user.username == listing.lister.username else False,                     # If user created post, this is true
        "closed": True if bid.listing.closed else False,
        "watchlist": watchlist
    })


@login_required
def bid(request):
    if request.method == "POST":
        bid = Bid.objects.get(pk=request.POST["bidID"])
        user = User.objects.get(username=request.user)

        try:
            newBid = int(request.POST["bid"])               # Make sure bid is an integer
        except ValueError:
            newBid = 0

        if newBid < bid.listing.item.price or (bid.numbids > 0 and newBid == bid.listing.item.price)\
        or bid.listing.lister == user:                                                                          # If bid is invalid, return error message
            return render(request, "auctions/message.html", {
                "title": "Error",
                "success": False
            })

        bid.numbids += 1
        bid.leader = user
        bid.listing.item.price = newBid                                     # If bid is valid, manipulate bid and item accordingly, return success message
        bid.listing.item.save()
        bid.save()

        return render(request, "auctions/message.html", {
            "title": "Success!",
            "success": True,
            "listing": bid.listing
        })

    return HttpResponseRedirect(reverse("index"))


@login_required
def close(request):
    if request.method == "POST":
        # Close a bid if its creator wants to close it
        bid = Bid.objects.get(pk=request.POST["bidID1"])
        bid.listing.closed = True
        bid.listing.save()
        return render(request, "auctions/message.html", {
            "title": "Bid Closed",
            "bid": bid
        })

    return HttpResponseRedirect(reverse("index"))


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