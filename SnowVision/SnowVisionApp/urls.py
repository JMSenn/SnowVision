from django.conf.urls import url
from SnowVisionApp import views

app_name ='SnowVisionApp'

urlpatterns= [
    url(r'^query_sherds/',views.sherd_search,name='query_database'),
    url(r'^query_designs/',views.design_search, name='query_designs'),
    url(r'^uploadSherd/',views.create_sherd_view,name='uploadSherd'),
    url(r'^updateSherd/(?P<pk>[-\w]+)/$',views.SherdUpdateView.as_view(),name ='updateSherd'),
    url(r'^deleteSherd/(?P<pk>[-\w]+)/$',views.SherdDeleteView.as_view(),name ='deleteSherd'),
    url(r'^create_context/',views.create_context_view,name='create_context'),
    url(r'^update_context/(?P<pk>[-\w]+)/$',views.ContextUpdateView.as_view(),name ="update_context"),
    url(r'^sherd_map/',views.sherd_map, name='sherd_map'),
    url(r'^site/(?P<pk>[-\w]+)/$', views.SiteDetailView.as_view(), name='site_detail'),
    url(r'^sherd/(?P<pk>[-\w]+)/$', views.SherdDetailView.as_view(), name='sherd_detail'),
    url(r'^design/(?P<pk>[-\w]+)/$', views.DesignDetailView.as_view(), name='design_detail'),
    url(r'^create_collection/$',views.create_collection_view, name="create_collection"),
    url(r'^deletecollection/(?P<pk>[-\w]+)/$',views.CollectionDeleteView.as_view(),name ='deletecollection'),

]

api_patterns = [
    url(r'^get_images/$', views.get_images, name = "get_images"),
    url(r'^get_csv/$', views.get_csv, name="get_csv"),
    url(r'^filter/project/$', views.filter_project, name="filter_project"),
    url(r'^filter/context/$', views.filter_context, name="filter_context"),
    url(r'^filter/collection/$', views.filter_collection, name="filter_collection"),

]

urlpatterns += api_patterns
