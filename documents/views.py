from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import simplejson
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
import tempfile
import itertools
import os
import psycopg2
from gis_apps import models
import csv
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from forms import ArticleForm
from documents.models import Article
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def documents(request):
    return render_to_response('documents.html')

def newpaper(request):
	return render_to_response('newpaper.html')

@csrf_exempt
def create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('showpaper')
    else:
        form = ArticleForm()

    args = {}
    args.update(csrf(request))

    args['form'] = form
    
    
    return render_to_response('documents.html',args)


@csrf_exempt
def showpaper(request):
    args = {}
    data = Article.objects.all()
    args["data"] = data
    return render_to_response('documents.html',args)

def papercontent(request, article_id = 1):
    return render_to_response('papercontent.html', {'article':Article.objects.get(id = article_id)})

    