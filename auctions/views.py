from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render,redirect
from django.urls import reverse
from django.forms import ModelForm

from .models import User,Auction,Bid,Comments,Description,Watchlist

# My Forms
class CreateListingForm(ModelForm):
    class Meta:
        model = Description
        fields = ["title","text","image","startingPrice","category"]

class biddingForm(ModelForm):
    class Meta:
        model = Bid
        fields = ["offerPrice"]

class comment_form(ModelForm):
    class Meta:
        model = Comments
        fields = ["comment"]

# Display listings 
def index(request, Category=None):
    # If category not None filter listings by category
    if Category == "search":
        Category = request.GET.get("Category")
        descriptions = Description.objects.filter(category=Category)
        return render(request, "auctions/index.html", {
            "descriptions": descriptions
        })
    # Else display all listings
    descriptions = Description.objects.all()
    return render(request, "auctions/index.html", {
        "descriptions": descriptions
    })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            next_url = request.POST.get("next_url")
            if next_url:
                return redirect(next_url)
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
        

def create_listing(request):
    
    # If request post get and validate form data
    if request.method == 'POST':
        form = CreateListingForm(request.POST,request.FILES)
        if form.is_valid():
            # If form is valid save but not to the database
            form = form.save(commit=False)
            auction = Auction(userId=request.user)# Create the auction by the user, save and then set it to the Description provided
            auction.save()
            form.itemSoldAs = auction
            # Save to the database
            form.save()
            return redirect("itemPage", form.id)
        # change this handle errors here
        else:
            code = "100: Invalid Form"
            message = "The form you submitted was invalid, Pls check to ensure all fields were filled properly"
            return redirect(f"/error?next={request.path}", {
            })
        
    # Else create a form and render
    form = CreateListingForm()
    return render(request, "auctions/newListing.html", {
        "form": form
    })
    
# Show items page
def itemPage(request, auctionId):
    # If auction is closed redirect to close
    auction = Auction.objects.get(pk=auctionId)
    Item = Description.objects.get(itemSoldAs=auctionId)
    if auction.closed == True:
        return redirect("close", auctionId)
    
    # If request method is post a bid is being placed
    if request.method == 'POST':
        if not request.user.id:
            return redirect(f"/login?next={request.path}")
        form = biddingForm(request.POST)
        
        # If user input is valid make sure it is higher than current and starting price
        if form.is_valid():
            offer = float(form["offerPrice"].value())
            start_price = Item.startingPrice
            current_price = Item.currentPrice
            
            if offer > start_price and offer > current_price:
                form = form.save(commit=False)
                form.userId = request.user
                form.item = Item.itemSoldAs
                form.save()
                
        return redirect("itemPage", Item.itemSoldAs.id)
        
    # Else just show the page
    form = biddingForm()
    # Get the auction id numbers and put in an iterable list to use in itemPage.html
    item_list = []
    if request.user.id:
        watchlistItems = list(Watchlist.objects.filter(userId=request.user).values_list('auctionId'))
        for i in watchlistItems:
            for j in i:
                item_list.append(j)
    
    return render(request, "auctions/itemPage.html", {
        "item": Item,
        "form": form,
        "watchlistItems": item_list,
        # display form for making comments and available comments
        "comment_form": comment_form(),
        "comments": Comments.objects.filter(commentOn=auctionId)
    })
    
# Render a persons watchlist
@login_required(login_url="/login")
def watchlist(request, itemId=None, remove=None):
    # If no item id provided show current watchlist
    if not itemId:
        # Get the watclist of the current user
        watchlist = Watchlist.objects.filter(userId=request.user)
        # Get the auction id from the list
        watchlistItems = list(watchlist.values_list('auctionId'))
        item_list = []
        for i in watchlistItems:
            for j in i:
                item_list.append(j)
        
        auctions = Description.objects.filter(itemSoldAs_id__in=item_list)
        return render(request, "auctions/watchlist.html", {
            "auctions": auctions
        })
        
    # Else if remove is None, add the item to the users watchlist
    itemId = Auction.objects.get(pk=itemId)
    if not remove:
        watch_list = Watchlist(userId=request.user,auctionId=itemId)
        watch_list.save()
        return redirect("watchlist")
        
    # Else remove from list
    to_delete = Watchlist.objects.filter(userId=request.user, auctionId=itemId)
    to_delete.delete()
    return redirect("watchlist")
    
# Close an auction
def close(request, auctionId):
    auction = Auction.objects.get(pk=auctionId)
    auction.closed = True
    auction.save()
    return render(request, "auctions/closed.html")
    
# Comments
def comment(request, auctionId):
    # Only allow logged in users comment
    if not request.user.id:
        return redirect(f"/login?next={request.path}")
        
    # Check form validity and add other needed fields
    form = comment_form(request.GET)
    if form.is_valid():
        form = form.save(commit=False)
        form.userId = request.user
        auction = Auction.objects.get(pk=auctionId)
        form.commentOn = auction
        form.save()
        
        # Redirect to item page
        return redirect("itemPage", auctionId)
    else:
        return HttpResponse("invalid form")