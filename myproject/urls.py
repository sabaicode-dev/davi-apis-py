"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from rest_framework import permissions
from drf_yasg.views import get_schema_view 
from drf_yasg import openapi

client_app = "http://localhost:3000"

schema_view = get_schema_view(
    openapi.Info( title="Davi Python API", 
                 default_version='v1', 
                 description=f"Test Davi Python backend. Visit [Support]({client_app}/contact) for details.",
                 terms_of_service=f"{client_app}/service", 
                 contact=openapi.Contact(
                     email="info@sabaicode.com", 
                     name="Davi Support", 
                     url=f"{client_app}/"
                     ), 
                 license=openapi.License(name="Copyright © 2024 DAVI. All rights reserved."), 
                 ), 
    public=True, 
    permission_classes=(permissions.AllowAny,), # permissions.AllowAny = allows all :)
)

urlpatterns = [ 
               path('admin/', admin.site.urls), 
               path('api/v1/', include('scrape.api.urls')), 
               path('api/v1/', include('cleansing.api.urls')), 
               path('api/v1/', include('file.api.urls')), 
               path('metafile/', include('metafile.api.urls')), 
               path('api/v1/', include('project.api.urls')), 
               path('api/v1/', include('visualization.api.urls')), 
               path('api/v1/', include('image_visualize.api.urls')), 
               path('api/v1/', include('aigeneratedes.api.urls')), 
               
               # Swagger URLs 
               path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'), 
               path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'), 
               path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'), 
            ]
