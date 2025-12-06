"""
URL routing configuration for the WorkoutWare project.

This module defines the URL patterns for the entire application.
It maps URL paths to their corresponding Django views, primarily by including
the URL configuration from the `workoutware_app` application.

Structure:
    - Admin site URLs
    - Core application URLs (from workoutware_app.urls)
    - Authentication URLs (login, logout)

All incoming HTTP requests are routed through this file.
"""
"""
URL configuration for workoutware project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('workoutware_app.urls')),
    path('admin/', admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls"))
]

from django.conf import settings
from django.conf.urls.static import static

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

