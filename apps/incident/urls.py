from django.urls import path

from .views import RetrieveIncident


urlpatterns = [
    path('incident/retrieve', RetrieveIncident.as_view())
]
