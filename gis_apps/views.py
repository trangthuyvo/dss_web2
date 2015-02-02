#!/usr/bin/python
# -*- coding: utf8 -*-
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
from django.views.decorators.csrf import csrf_exempt


def get_filepaths(directory):
    """
    This function will generate the file names in a directory 
    tree by walking the tree either top-down or bottom-up. For each 
    directory in the tree rooted at directory top (including top itself), 
    it yields a 3-tuple (dirpath, dirnames, filenames).
    """
    file_paths = []  # List which will store all of the full filepaths.

    # Walk the tree.
    for root, directories, files in os.walk(directory):
        for filename in files:
            # Join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)  # Add it to the list.

    return file_paths  # Self-explanatory.


def gisbase(request):
    
    return render_to_response('gisbase.html')
    
def province(request):
    from vectorformats.Formats import Django, GeoJSON
    #   Add province
    data = models.province_boundary.objects.all()
    djf = Django.Django(geodjango="geometry", properties = ["id","province"])
    geoj = GeoJSON.GeoJSON()
    provinces = geoj.encode(djf.decode(data))

#    return render_to_response('gisbase.html',args)
    return HttpResponse(provinces)

def update_geojson(request):
    from vectorformats.Formats import Django, GeoJSON
    # Get data from postgres and convert to geojason format
    stations_data = models.stations.objects.all()
    stations_djf = Django.Django(geodjango="geometry", properties = ["id","name"])
    stations_geoj = GeoJSON.GeoJSON()
    stations_geojs_string = stations_geoj.encode(stations_djf.decode(stations_data))
    
    
    provinces_data = models.province_boundary.objects.all()
    provinces_djf = Django.Django(geodjango="geometry", properties = ["id","province"])
    provinces_geoj = GeoJSON.GeoJSON()
    provinces_geojs_string = provinces_geoj.encode(provinces_djf.decode(provinces_data))

    landuse_data = models.landuse.objects.all()
    landuse_djf = Django.Django(geodjango="geometry", properties = ["id","code"])
    landuse_geoj = GeoJSON.GeoJSON()
    landuse_geojs_string = landuse_geoj.encode(landuse_djf.decode(landuse_data))
    
    # Get dir path
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    FILE_DIR = os.path.join(BASE_DIR, 'media/geojson/')
    
    
     # Delete all of old geojson file
    file_paths = get_filepaths(FILE_DIR)
    
    if file_paths != []:
        for element in file_paths:
            os.remove(element)
        
    ## Write new geojason file    
    
    stations_geojson = open(FILE_DIR+"stations.js", "w")
    stations_geojson.write(stations_geojs_string)
    stations_geojson.close()
    
    provinces_geojson = open(FILE_DIR+"provinces.js", "w")
    provinces_geojson.write(provinces_geojs_string)
    provinces_geojson.close()
    
    landuse_geojson = open(FILE_DIR+"landuse.js", "w")
    landuse_geojson.write(landuse_geojs_string)
    landuse_geojson.close()
    
    
    args = []
    return render_to_response('database.html',args)
    


def stations(request):
    from vectorformats.Formats import Django, GeoJSON
    #   Add province
    data = models.stations.objects.all()
    djf = Django.Django(geodjango="geometry", properties = ["id","name"])
    geoj = GeoJSON.GeoJSON()
    stations = geoj.encode(djf.decode(data))

#    return render_to_response('gisbase.html',args)
    return HttpResponse(stations)



def some_view(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response


@ensure_csrf_cookie
@csrf_exempt
def data_review(request):
    args ={}
    args.update(csrf(request)) 
    id_list = request.POST.getlist('id[]',[0,0,0,0])
    name_list = request.POST.getlist('name[]',[0,0,0,0])
    id_list = list(id_list)
    n = len(id_list)

    
    # connect with server
    connection = psycopg2.connect(dbname="dss2", user="postgres", password="", host ="localhost", port ="5432")
    connection.commit()
    
    data_dict = {}
    
    for i in range(n):
        variable_list = []
        starttime_list = []
        endtime_list = []
        
        data = connection.cursor()
        data.execute('SELECT "VariableName","BeginDateTime","EndDateTime" FROM dbo."SeriesCatalog" WHERE "SiteID" = ' + str(int(id_list[i])))
        data = data.fetchall()
        
        for element in data:
            variable_list.append(str(element[0]))
            starttime_list.append(str(element[1]))
            endtime_list.append(str(element[2]))
            
        data_dict.update({id_list[i]:zip(variable_list,starttime_list,endtime_list)})
        
      
    args['name_list'] = name_list        
    args['id_list'] = id_list
    args['data_dict'] = data_dict
    
    return render_to_response('data-review.html',args)

#@ensure_csrf_cookie
@csrf_exempt
def data_download(request):
    import os
    import zipfile
    import StringIO
    import csv
    from time import time
    # Make a variable id dictonary
    selected_id = request.POST.getlist('selected_id[]',[0,0,0,0])
    selected_variable = request.POST.getlist('selected_variable[]',[0,0,0,0])
    selected_starttime = request.POST.getlist('selected_starttime[]',[0,0,0,0])
    selected_endtime = request.POST.getlist('selected_endtime[]',[0,0,0,0])
        
        

    connection = psycopg2.connect(dbname="dss2", user="postgres", password="", host ="localhost", port ="5432")
    connection.commit()
    variable_dictonary = {}
    variable_data = connection.cursor()
    variable_data.execute('SELECT "VariableName","VariableID" FROM dbo."Variables"')
    connection.commit()
    variable_data = variable_data.fetchall()
    for element in variable_data:
        variable_dictonary.update({(element[0]).rstrip():element[1]})
    n = len(selected_variable)
    
    url = "/media/download_file" +"/"+str(time()).replace(".","_")+ "_myfile.zip"
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    FILE_DIR = os.path.join(BASE_DIR, 'media/download_file')
                               
    zipfile = zipfile.ZipFile(BASE_DIR + url, "w")
    


    for i in range(n):
        data = connection.cursor()
        data.execute('SELECT "LocalDateTime","DataValue" FROM dbo."DataValues" WHERE "SiteID" = '
                     +str(int(selected_id[i])) + ' AND "VariableID" = ' 
                     +str(variable_dictonary[(selected_variable[i]).rstrip()]) 
                     + ' AND "LocalDateTime" >' 
                     + "'"+str(selected_starttime[i])+"'" 
                     + ' AND "LocalDateTime" < '
                     + "'"+str(selected_endtime[i]) + "'")
        connection.commit()
        data = data.fetchall()


        csv_filename = str(selected_id[i])+"_"+str(selected_variable[i].rstrip())+"_"+str(selected_starttime[i])+"_"+str(selected_endtime[i])+'.csv'
        
        
        csv_out = StringIO.StringIO()
#         create the csv writer object.
        mywriter = csv.writer(csv_out)
        mywriter.writerow(["Date","Value"])
        for row in data:
            mywriter.writerow([row[0], row[1]])
            
        zipfile.writestr(csv_filename,csv_out.getvalue())
        csv_out.close()
        
    zipfile.close()
    return HttpResponse(url)

def data_download2(request):
    return request
    
