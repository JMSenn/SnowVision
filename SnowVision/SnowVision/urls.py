"""SnowVision URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views

from SnowVisionApp import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(),name='index'),
    url(r'^admin/', admin.site.urls),
#    url(r'^login/$', views.NoLoginView.as_view(), name='login'),
    url(r'^login/$', views.NoPageView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView, {'next_page': 'login'}, name='logout'),
#    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup/$', views.NoPageView.as_view(), name='signup'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
    views.activate, name='activate'),
#    url(r'^profile/$', views.user_profile, name='user_profile'),
    url(r'^login/$', views.NoPageView.as_view(), name='user_profile'),
    url(r'^collection/(?P<pk>[-\w]+)/$',views.CollectionDetailView.as_view(), name = "collectiondetail"),
    url(r'^about/', views.AboutView.as_view(),name='about'),
    url(r'^snowvision/',include('SnowVisionApp.urls',namespace='SnowVisionApp')),
    url(r'^references/$',views.ResearchView.as_view(), name='research'),
    url(r'^algorithm/$', views.AlgorithmView.as_view(), name='algorithm'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
