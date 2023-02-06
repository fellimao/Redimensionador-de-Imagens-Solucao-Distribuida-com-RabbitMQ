from django.urls import path, include
from rest_framework import routers
from .views import *
from django.conf.urls.static import static
from django.conf import settings

router = routers.DefaultRouter()

router.register(r'imaging', ImagemViewSet, basename="imaging")

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)