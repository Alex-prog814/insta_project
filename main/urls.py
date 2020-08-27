from django.urls import path

from . import views


urlpatterns = [
    path('followers/', views.FollowersList.as_view()),
]