# REST FRAMEWORK
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.filters import SearchFilter

# Cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

# Custom Models
from news.models import Country, Source, Category, Article

# Custom Serializers
from news.serializers import ArticlesListSerializer

# Others
import requests
from datetime import date, timedelta
from config.config import CATEGORIES, COUNTRIES, BASE_NEWS_URL


def create_article(article, country, category_name):
    source_name = article.get("source").get("name")
    source_obj = Source.objects.get_or_create(name=source_name)[0]
    country_obj = Country.objects.get_or_create(name=country)[0]
    category_obj = Category.objects.get_or_create(name=category_name)[0]

    objs = Article.objects.filter(url=article.get("url"))

    if not objs:
        Article.objects.create(
            source=source_obj,
            category=category_obj,
            country=country_obj,
            title=article.get("title"),
            author=article.get("author"),
            description=article.get("description"),
            url=article.get("url"),
            urlToImage=article.get("urlToImage"),
            publishedAt=article.get("publishedAt"),
        )

    return True


class FetchNews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):

        for country in COUNTRIES:

            # Top News
            url = f"{BASE_NEWS_URL}&country={country}"

            response = requests.get(url).json()

            for article in response.get("articles"):
                create_article(article, country, "top")

            # Category Based News
            for category_name in CATEGORIES:
                url = f"{BASE_NEWS_URL}&country={country}&category={category_name}"

                response = requests.get(url).json()

                for article in response.get("articles"):
                    create_article(article, country, category_name)

        return Response({"status": True})


class DeleteOldNews(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        old_news = Article.objects.filter().exclude(publishedAt__date__range=[date.today() - timedelta(days=3), date.today()])
        old_news.delete()

        return Response({"status": f"{old_news.count()} news are deleted!"})


class News(ListAPIView):
    serializer_class = ArticlesListSerializer
    filter_backends = (SearchFilter,)
    search_fields = ("title",)

    def get_queryset(self):
        queryset = Article.objects.filter().order_by("-publishedAt")

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category__name=category)

        return queryset

    # Cache page for the requested url
    @method_decorator(cache_page(60 * 15))
    def get(self, *args, **kwargs):
        return super().get(*args, **kwargs)