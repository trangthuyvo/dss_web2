from django.conf.urls import patterns, include, url

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'dss.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
   url(r'^$', 'home.views.index'),
   url(r'^admin/', include(admin.site.urls)),
   url(r'^gis/', include('gis_apps.urls')),
   url(r'^database/', include('database.urls')),
   url(r'^contact/', 'home.views.contact'),
   url(r'^database/', 'home.views.database'),
   url(r'^documents/', include('documents.urls')),
)+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
