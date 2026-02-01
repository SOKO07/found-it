from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = "lnf"
urlpatterns = [
    path("", views.full_info, name="landing"),
    path("home/", views.index, name="index"),
    path('api/items/', views.items_api, name='items_api'),
    path("upload/", views.upload, name="upload"),
    path("profile/", views.profile, name="profile"),
    path('about/', views.about, name='about'),
    path('features/', views.features, name='features'),
    path('contact/', views.contact, name='contact'),

    path("signup/", views.signup, name="signup"),
    path("login/", views.Login.as_view(), name="login"), # Custom Login View
    path('logout/', auth_views.LogoutView.as_view(next_page='lnf:landing'), name='logout'),
    path("item/<int:item_id>/toggle_watch/", views.toggle_watch_item, name="toggle_watch_item"),
    path('item/<int:item_id>/delete/', views.delete_item, name='delete_item'),
    path('go_to_my_uploads/', views.go_to_my_uploads, name='go_to_my_uploads'),
]
