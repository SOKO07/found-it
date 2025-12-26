from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "lnf"
urlpatterns = [
    path("", views.index, name="index"),
    path('api/items/', views.items_api, name='items_api'),
    path("upload/", views.upload, name="upload"),
    path("profile/", views.profile, name="profile"),

    path("signup/", views.signup, name="signup"),
    path("login/", views.Login.as_view(), name="login"), # Custom Login View
    path('logout/', auth_views.LogoutView.as_view(next_page='lnf:index'), name='logout'),
    path("<int:item_id>/watch/", views.watch_item, name="watch_item"),
    path("<int:item_id>/unwatch/", views.unwatch_item, name="unwatch_item"),
]
