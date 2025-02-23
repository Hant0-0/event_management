from django.contrib import admin
from django.urls import path, include
from event_api.swagger import urlpatterns as swagger_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include("event_api.urls")),
]

urlpatterns += swagger_urls