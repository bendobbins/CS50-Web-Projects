import os
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse

from .models import User


SPORTS = ["Basketball", "Football", "Soccer", "Baseball", "Tennis", "Golf", "Hockey", "Bowling", "Rugby",
"Table Tennis", "Weight Training", "Cycling", "Running", "Yoga"]
TYPES = ["Tournament", "Exhibition", "Training/Practice"]
COMPETITION = ["Casual", "Moderate", "Competitive", "N/A"]



def index(request):
    return render(request, "sports/index.html", {
        "sports": SPORTS
    })


def sport(request, sport):
    return render(request, "sports/index.html", {
        "sports": SPORTS,
        "sport": sport
    })


@login_required
def create(request):
    return render(request, "sports/create.html", {
        "sports": SPORTS,
        "types": TYPES,
        "competition": COMPETITION
    })


def profile(request, name):
    person = {
        "username": name,
        "picture": os.path.join(os.getcwd(), "/static/sports/blank.jpg"),
        "name": User.objects.get(username=request.user.username).name
        }
    return render(request, "sports/profile.html", {
        "person": person,
        "sports": SPORTS
    })


@login_required
def upload(request):
    if request.method != "POST":
        return render(request, "sports/index.html", {
            "sports": SPORTS
        })

    try:
        print(request.FILES["image-upload"])
    except:
        print("failed")
    try:
        print(request.FILES["image-form"])
    except:
        print("failed")
    try:
        print(request.POST["image-upload"])
    except:
        print("failed")
    try:
        print(request.POST["image-form"])
    except:
        print("failed")
    return render(request, "sports/index.html", {
        "sports": SPORTS
    })


@login_required
def update_profile(request):
    return render(request, "sports/update_profile.html")


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
            return render(request, "sports/login.html", {
                "error": "Invalid username and/or password."
            })
    return render(request, "sports/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        name = request.POST["name"]
        username = request.POST["username"]
        email = request.POST["email"]
        age = request.POST["age"]

        if len(username) > 32 or len(username) < 1:
            return render(request, "sports/register.html", {
                "error": "Username must be 32 characters or less."
            })

        try:
            age = int(age)
            if age < 18:
                return render(request, "sports/register.html", {
                    "error": "You must be 18 to use this site."
                })
        except ValueError:
            return render(request, "sports/register.html", {
                "error": "Enter valid age."
            })

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "sports/register.html", {
                "error": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, name=name, age=age)
            user.save()
        except IntegrityError:
            return render(request, "sports/register.html", {
                "error": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    return render (request, "sports/register.html")