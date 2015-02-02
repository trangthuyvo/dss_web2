from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^documents$','documents.views.documents'),
                       url(r'^newpaper$','documents.views.newpaper'),
                       url(r'^create$','documents.views.create'),
                       url(r'^showpaper$','documents.views.showpaper'),
                       url(r'^papercontent$','documents.views.papercontent'),
                       url(r'^(?P<article_id>\d+)/$','documents.views.papercontent'),
                       )
