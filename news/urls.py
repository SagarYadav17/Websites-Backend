from django.urls import path
from news import views

urlpatterns = [
    path("fetch-news/", views.FetchNews.as_view(), name="fetch-news"),
    path("delete-news/", views.DeleteOldNews.as_view(), name="delete-news"),
    path("news/", views.NewsView.as_view(), name="news"),
]
