from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("register", views.register, name="register"),
    path("logout", views.logout_view, name="logout"),
    path("create", views.create, name="create"),
    path("upload", views.upload, name="upload"),
    path("profile/<str:name>", views.profile, name="profile"),
    path("update", views.update_profile, name="update"),
    path("<str:sport>", views.sport, name="sport")
]