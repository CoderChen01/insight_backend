from django.urls import path

from .views import *

urlpatterns = [
    path("ai-skill-group/create", CreateInterfaceGroup.as_view()),
    path("ai-skill-group/retrieve", RetrieveInterfaceGroup.as_view()),
    path("ai-skill-group/update", UpdateInterfaceGroup.as_view()),
    path("ai-skill-group/delete", DeleteInterfaceGroup.as_view()),
    path("ai-skill/create", CreateInterface.as_view()),
    path("ai-skill/retrieve", RetrieveInterface.as_view()),
    path("ai-skill/update", UpdateInterface.as_view()),
    path("ai-skill/delete", DeleteInterface.as_view()),
    path("ai-skill/update-state", RefreshState.as_view()),
]
