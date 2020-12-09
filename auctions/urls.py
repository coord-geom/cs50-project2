from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("categories", views.categories, name="categories"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("my_listings", views.my_listings, name="my_listings"),
    path("listings/<int:ID>", views.listings, name="listing")
]

