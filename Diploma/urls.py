"""
URL configuration for Diploma project.

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

from django.conf import settings
from django.conf.urls.static import static
from converter import views
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('medical/admin')
    path('', views.app_render, name="converter"),
    path('medical/app/history',views.converter_history, name="converter_history"),
    path('medical/app/custom-downloader/',views.get_images_by_ids, name="get_images_by_ids"),
    path('process.ajax',views.ajax_server, name="ajax_server"),
    path('medical/image-classification', views.get_image_classification, name="get_image_classification"),
    path('material-selector/', include('material_selector.urls')),
    path('stats/', views.client_statistics, name="stats"),
    
    path('admin/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
