from django.urls import path

from .views import RetrieveIncident, DeleteIncident, DeleteAllIncidents


urlpatterns = [
    path('incident/retrieve', RetrieveIncident.as_view())
    # path('incident/delete', DeleteIncident.as_view()),
    # path('incident/delete-all-incidents', DeleteAllIncidents.as_view())
]
