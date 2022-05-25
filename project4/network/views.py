import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
import datetime

from .models import Following, Like, User, Post


def index(request):
    page = paginator(Post.objects.all().order_by("-timestamp").all(), request)
    return render(request, "network/index.html", {
        "posts": page,      # Page of at most 10 posts
        "liked": get_user_likes(request)        # List of ids of posts that user liked
    })


@login_required
def new(request):
    if request.method == "POST":
        post = request.POST["post"]
        if post:                # If post has content, save it as a new post
            Post(user=User.objects.get(username=request.user), content=post, timestamp=datetime.datetime.now()).save()
            return HttpResponseRedirect(reverse("index"))

    return render(request, "network/new.html")


@login_required
def edit(request):
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required"}, status=400)
    
    data = json.loads(request.body)
    try:
        # Change content of post with id from data
        post = Post.objects.get(pk=data.get("id")) 
        if request.user != post.user:               # If user is trying to edit a post that is not theirs, return an error
            return JsonResponse({"error": "You are not allowed to edit that post."}, status=400)
        post.content = data.get("content")
        post.save()
        return JsonResponse({"message": "Success"}, status=204)

    except Post.DoesNotExist:
        return JsonResponse({"error": "Post does not exist."}, status=400)


@login_required
def like(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    data = json.loads(request.body)
    try:
        post = Post.objects.get(pk=data.get("id"))
        # If post was liked, add a new Like entry for it and add 1 to post likes
        if data.get("liked"):
            Like(liker=request.user, post=post).save()
            post.likes += 1
        # If post was unliked, delete Like entry for it and subtract 1 from likes
        else:
            Like.objects.filter(liker=request.user, post=post).delete()
            post.likes -= 1
        post.save()
        return JsonResponse({"message": "Success"}, status=201)

    except Post.DoesNotExist:
        return JsonResponse({"error": "Post does not exist"}, status=400)


def profile(request, username):
    person = User.objects.filter(username=username)
    if person:                              # Make sure user is visiting profile of another valid user

        user = User.objects.get(username=username)
        followed = False
        try:
            # Check if user is following the person whos profile they are visiting
            for following in User.objects.get(username=request.user).userFollowings.all():
                if following.followed.username == username:
                    followed = True
        except User.DoesNotExist:
            pass

        page = paginator(Post.objects.filter(user=user).order_by("-timestamp").all(), request)

        return render(request, "network/profile.html", {
            "person": user,
            "posts": page,
            "following": followed,
            "valid": True,
            "liked": get_user_likes(request)
        })

    # If profile being visited is not a valid user, return template with no args
    return render(request, "network/profile.html")


@login_required
def following(request):
    user = User.objects.get(username=request.user)
    # For user following/unfollowing other user
    if request.method == "POST":
        data = json.loads(request.body)
        follow = False

        try:            # If user is trying to follow themselves or another user that does not exist, return error
            followed = User.objects.get(username=data.get("followed"))
            if followed == user:
                raise User.DoesNotExist
        except User.DoesNotExist:
            return JsonResponse({
                "followed": False,
                "unfollowed": False,
            }, status=400)

        # If user is not already following the other user, create a new following object and add 1 to corresponding values in each user object
        if not Following.objects.filter(follower=user, followed=followed):
            Following(follower=user, followed=followed).save()
            followed.followers += 1
            user.following += 1
            follow = True
        # If user is following other user, delete object and subtract from corresponding values
        else:
            Following.objects.filter(follower=user, followed=followed).delete()
            followed.followers -= 1
            user.following -= 1
        followed.save()
        user.save()

        return JsonResponse({
            "followed": follow,
            "unfollowed": not follow,
            "followers": followed.followers
        }, status=201)

    # GET method (for retrieving following page)

    followed = user.userFollowings.all()            # Get all following objects in which user is follower

    peopleFollowed = []
    for following in followed:
        peopleFollowed.append(following.followed)       # Make a list of user objects that the user is following

    posts = []
    for person in peopleFollowed:
        for post in person.userPosts.all():             # Make a list of all posts by followed users
            posts.append(post)

    posts = sorted(posts, key=lambda instance: instance.timestamp, reverse=True)        # Sort list by timestamp

    page = paginator(posts, request)

    return render(request, "network/index.html", {
        "following": True,
        "posts": page,
        "liked": get_user_likes(request)
    })


def get_user_likes(request):
    """
    Given a page request made by some user, return a list of ids referring to all posts liked by that user (if any).
    """
    likes = []
    try:
        userLiked = User.objects.get(username=request.user).userLikedPosts.all()        # Get all Like objects where user is liker
        for like in userLiked:
            likes.append(like.post.id)          # Make list of ids
    except User.DoesNotExist:
        pass
    return likes


def paginator(posts, request):
    """
    Given a list of posts and a page request, paginate the list and return a list of the 10 posts (max) to be displayed on the page the user requested.
    """
    paginated = Paginator(posts, 10)
    pageNumber = request.GET.get("page")
    page = paginated.get_page(pageNumber)
    return page


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
