"""ADCat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # path("admin/", admin.site.urls),
    path('adbench_choose_algo/', views.upload_file),
    path('adbench_result/', views.show_result),
    path('service1_result/', views.service1_result),
    path('adgym_re1/', views.adgym_re1),
    path('adgym_re2/', views.adgym_re2, name='adgym_goon')
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
