from django.urls import path

from . import views

app_name = "lnf"
urlpatterns = [
    path("", views.index, name="index"),
    path('api/items/', views.items_api, name='items_api'),
    path("upload/", views.upload, name="upload"),
    path("base/", views.base, name="base"),
    path("signup/", views.signup, name="signup"),
    path("<int:item_id>/hold/", views.hold_item, name="hold_item"),
    path("<int:item_id>/unhold/", views.unhold_item, name="unhold_item"),
]