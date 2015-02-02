from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^basemap$','gis_apps.views.gisbase'),
                       url(r'^province$','gis_apps.views.province'),
                       url(r'^stations$','gis_apps.views.stations'),
                       url(r'^csv$','gis_apps.views.some_view'),   
                       url(r'^data_review$','gis_apps.views.data_review'),
                       url(r'^data_download$','gis_apps.views.data_download'),
                       url(r'^update_geojson$','gis_apps.views.update_geojson'),
                       )
