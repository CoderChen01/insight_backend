from django.urls import path

from .views import *

urlpatterns = [
    path("face-group/create", CreateFaceGroup.as_view()),
    path("face-group/retrieve", RetrieveFaceGroup.as_view()),
    path("face-group/update", UpdateFaceGroup.as_view()),
    path("face-group/delete", DeleteFaceGroup.as_view()),
    path("face/create", CreateFace.as_view()),
    path("face/retrieve", RetrieveFace.as_view()),
    path("face/update", UpdateFace.as_view()),
    path("face/delete", DeleteFace.as_view()),
]
