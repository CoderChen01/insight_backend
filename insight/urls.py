"""insight URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path

urlpatterns = [
    path("api/v1/user-management/", include("user.urls")),
    path("api/v1/camera-management/", include("camera.urls")),
    path("api/v1/face-management/", include("face.urls")),
    path("api/v1/interface-management/", include("interface.urls")),
    path("api/v1/incident-management/", include("incident.urls")),
]
