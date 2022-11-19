from django.urls import path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path(
        "classifications/",
        views.ClassificationView.as_view(),
        name="classification_list",
    ),
    path("upload/", views.upload_file, name="upload"),
    path(
        "upload_classifications/",
        views.upload_classifications,
        name="upload_classifications",
    ),
    path("home/", views.home, name="home"),
]
