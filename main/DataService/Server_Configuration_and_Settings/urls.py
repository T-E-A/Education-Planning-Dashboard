"""
URL configuration for DataLayer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

# By: Tejas Kumar
# This module is where we declare the entry point for the public facing API. 
# In the URL Patterns object we simply have to include the 'urls.py' module in the 'urlpatterns' object. 

from django.contrib import admin
from django.urls import path, include

# wire up the admin panel and include all API_Elements routes at the root
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('API_Elements.urls'))
]
