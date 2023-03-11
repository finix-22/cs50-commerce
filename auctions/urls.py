from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("createlisting", views.create_listing, name="create_listing"),
    path("comment/<int:auctionId>", views.comment, name="comment"),
    path("close/<int:auctionId>", views.close, name="close"),
    path("<int:auctionId>", views.itemPage, name="itemPage"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("watchlist/<int:itemId>", views.watchlist, name="watchlist"),
    path("watchlist/<int:itemId>/<str:remove>", views.watchlist, name="watchlist"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:Category>", views.index, name="index"),
]
