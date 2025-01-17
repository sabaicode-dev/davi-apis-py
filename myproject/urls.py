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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('scrape.api.urls')),
    # upload & cleansing dataset 
    path('api/v1/', include('cleansing.api.urls')),
    # get files updated
    path('api/v1/', include('file.api.urls')),

    path('api/v1/metafile/', include('metafile.api.urls')),
    
    # create new project
    path('api/v1/', include('project.api.urls')),
    
    path('api/v1/', include('visualization.api.urls')),

    path('api/v1/', include('image_visualize.api.urls')),
    
    path('api/v1/', include('aigeneratedes.api.urls')),
]