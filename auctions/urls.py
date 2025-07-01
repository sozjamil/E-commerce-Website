from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from . import views


urlpatterns = [
    path("all_category/<int:category_id>", views.show_category, name="show_category"),
    path("all_category", views.all_category, name="all_category"),
    path("close_listing/<int:listing_id>/", views.close_listing, name="close_listing"),
    path("add_bid/<int:listing_id>/", views.add_bid, name="add_bid"),
    path("add_comment/<int:listing_id>/", views.add_comment, name="add_comment"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("add_watchlist/<int:listing_id>/",views.add_watchlist, name="add_watchlist"),
    path("remove_watchlist/<int:listing_id>/",views.remove_watchlist, name="remove_watchlist"),
    path("singlelisting/<int:listing_id>/",views.single_listing, name="single_listing"),
    path("create", views.create_listing, name="create"),
    path('search/', views.search, name='search'),


    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
