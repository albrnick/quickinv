from django.conf.urls import patterns, include, url

import views

urlpatterns = patterns('',
    url(r'^$', views.system_inventory_overview, name='home'),
    url(r'^view/$', views.inventory_view, name='inventory_view'),
    url(r'^view_systems/$', views.system_inventory_view, name='system_inventory_view'),
    url(r'^item/add/$', views.item_add_edit, name='item_add'),
    url(r'^item/edit/(?P<id>\d+)/$', views.item_add_edit, name='item_edit'),
    url(r'^system/build/$', views.system_build, name='system_build'),
    url(r'^system/view/(?P<id>\d+)/$', views.item_view, name='system_view'),
)
