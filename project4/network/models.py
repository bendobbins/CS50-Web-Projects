from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.PositiveIntegerField(default=0)
    following = models.PositiveIntegerField(default=0)

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userPosts")
    content = models.CharField(max_length=1000)
    timestamp = models.DateTimeField()
    likes = models.PositiveIntegerField(default=0)

class Following(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userFollowings")
    followed = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userFollowed")

class Like(models.Model):
    liker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="userLikedPosts")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="allLikedPosts")