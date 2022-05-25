from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:entry>", views.wiki_page, name="wiki"),
    path("random", views.rand, name="random"),
    path("create", views.create, name="creator"),
    path("edit", views.edit, name="editor"),
    path("save", views.save, name="save")
]
