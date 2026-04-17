from django.urls import path
from . import views

urlpatterns = [
    path("entries/", views.entries_list_create, name="entries-list-create"),
    path("entries/<int:entry_id>/", views.entry_detail_update, name="entry-detail-update"),
]
