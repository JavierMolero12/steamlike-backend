from django.urls import path
from . import views

urlpatterns = [
    path("search/", views.catalog_search, name="catalog-search"),
    path("resolve/", views.catalog_resolve, name="catalog-resolve"),
]
