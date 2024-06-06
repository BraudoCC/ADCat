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
from django.urls import path, include
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path('home/', views.home, name='home'),
    path('adbench/', views.adbench, name='adbench'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('online-training/', views.service1, name='service1'),
    path('adgym/', views.adgym, name='adgym'),

    path('', include('login_func.urls')),
    path('', include('adbench_upload.urls')),

    path('unsupervised_info/', views.PCA, name='unsupervised'),
    path('unsupervised_info_OCSVM/', views.OCSVM, name='OCSVM'),
    path('unsupervised_info_LOF/', views.LOF, name='LOF'),
    path('unsupervised_info_CBLOF/', views.CBLOF, name='CBLOF'),
    path('unsupervised_info_COF/', views.COF, name='COF'),
    path('unsupervised_info_HBOS/', views.HBOS, name='HBOS'),
    path('unsupervised_info_KNN/', views.KNN, name='KNN'),
    path('unsupervised_info_SOD/', views.SOD, name='SOD'),
    path('unsupervised_info_COPOD/', views.COPOD, name='COPOD'),
    path('unsupervised_info_ECOD/', views.ECOD, name='ECOD'),
    path('unsupervised_info_DeepSVDD/', views.DeepSVDD, name='DeepSVDD'),
    path('unsupervised_info_DAGMM/', views.DAGMM, name='DAGMM'),
    path('unsupervised_info_LODA/', views.LODA, name='LODA'),
    path('unsupervised_info_IForest/', views.IForest, name='IForest'),

    path('semi-supervised_info/', views.GANomaly, name='semi-supervised'),
    path('semi-supervised_info_DeepSAD/', views.DeepSAD, name='DeepSAD'),
    path('semi-supervised_info_REPEN/', views.REPEN, name='REPEN'),
    path('semi-supervised_info_DevNet/', views.DevNet, name='DevNet'),
    path('semi-supervised_info_PReNet/', views.PReNet, name='PReNet'),
    path('semi-supervised_info_FEAWAD/', views.FEAWAD, name='FEAWAD'),
    path('semi-supervised_info_XGBOD/', views.XGBOD, name='XGBOD'),

    path('supervised_info/', views.NB, name='supervised'),
    path('supervised_info_SVM/', views.SVM, name='SVM'),
    path('supervised_info_MLP/', views.MLP, name='MLP'),
    path('supervised_info_RF/', views.RF, name='RF'),
    path('supervised_info_XGBoost/', views.XGBoost, name='XGBoost'),
    path('supervised_info_LightGBM/', views.LightGBM, name='LightGBM'),
    path('supervised_info_CatBoost/', views.CatBoost, name='CatBoost'),
    path('supervised_info_ResNet/', views.ResNet, name='ResNet'),
    path('supervised_info_FTTransformer/', views.FTTransformer, name='FTTransformer'),

    path('', views.home, name='index'),

]
