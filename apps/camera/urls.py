from django.urls import path

from .views import *

urlpatterns = [
    path("camera-group/create", CreateCameraGroup.as_view()),
    path("camera-group/retrieve", RetrieveCameraGroup.as_view()),
    path("camera-group/update", UpdateCameraGroup.as_view()),
    path("camera-group/delete", DeleteCameraGroup.as_view()),
    path("camera/create", CreateCamera.as_view()),
    path("camera/retrieve", RetrieveCamera.as_view()),
    path("camera/update", UpdateCamera.as_view()),
    path("camera/delete", DeleteCamera.as_view()),
    path("camera/set-extraction-settings", SetExtractFrameSettings.as_view()),
    path("camera/preview", CameraPreview.as_view()),
    path("camera/video-preview", VideoPreview.as_view()),
    path("camera/set-ai-skill-settings", SetAISkillSettings.as_view()),
    path("camera/start-task", Start.as_view()),
    path("camera/stop-task", Stop.as_view()),
]
