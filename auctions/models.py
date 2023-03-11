from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY = (
    ("clothes","Clothes"),
    ("books","Books"),
    ("TV","Television"),
    ("digital","Digital"),
    ("phones","Phones"),
    ("laptop","Laptop")
)

class User(AbstractUser):
    id = models.AutoField(primary_key=True)
    pass

# Keeping track of auctions
class Auction(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctioneer")
    closed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.id} {self.userId}"
    
# Keeping info on items
class Description(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=40)
    text = models.TextField()
    image = models.ImageField(upload_to="images")
    startingPrice = models.FloatField()
    currentPrice = models.FloatField(default=0)
    category = models.CharField(max_length=25,choices=CATEGORY,null=True)
    itemSoldAs = models.OneToOneField(Auction, on_delete=models.CASCADE, related_name="saleAs")
    
    def __str__(self):
        return f"{self.itemSoldAs}: {self.title}"
    
# Keeping track of bids made
class Bid(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name="buyer")
    offerPrice = models.FloatField()
    item = models.ForeignKey(Auction, null=True, on_delete=models.CASCADE, related_name="purchase")
    
    def __str__(self):
        return f"{self.userId} bids on item ({self.item})"
    
# Keeping track of comments made
class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="thought")
    comment = models.CharField(max_length=500)
    commentOn = models.ForeignKey(Auction, null=True, on_delete=models.SET_NULL, related_name="commentedOn")                                #f
    
    def __str__(self):
        return f"{self.userId}'s Comment about item({self.commentOn})"
        
# Keeping track of peoples watchlists
class Watchlist(models.Model):
    id = models.AutoField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.CASCADE, related_name="usersWatchist")
    auctionId = models.ForeignKey(Auction, null=True, on_delete=models.SET_NULL, related_name="itemOnList")