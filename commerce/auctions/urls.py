from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="creator"),
    path("listing/<int:id>", views.listing, name="listing"),
    path("bid", views.bid, name="bid"),
    path("close", views.close, name="close"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("categories", views.categories, name="categories")
]