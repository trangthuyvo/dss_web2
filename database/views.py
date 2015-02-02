#!/usr/bin/python
# -*- coding: utf8 -*-

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template.loader import render_to_string
import os
import simplejson
import itertools
from django.contrib.gis.geos import Point
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
import tempfile
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import csv
import numpy as np
from datetime import datetime
import ogr, osr
import pandas
from forms import UploadForm


################################################################################################
################################################################################################
################################################################################################
################################################################################################
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


def importseriesdata(request):
    
    return render_to_response('importseriesdata.html')


def format_data(data):
    try:
        int(data)
        return str(data)
    except:
        if data == "" or data == "NULL" or data == "Null" or data == "null" or data == None:
            data = "NULL"
        else:
            data = "'" + data + "'"

        return str(data)

class reading_csv():
    def __init__(self,DataName):
        self.DataName = DataName
    def read(self,init_row=1,init_col=1):
        Array_Data = []
        
        f = open(self.DataName,'rb')
        csv_data = csv.reader(f)
        Header = next(csv_data)
        n_column = len(Header)
        i = 0
        for row in csv_data:
            i = i + 1
            if i >= (init_row-1):
                float_row = [element for element in row]
                Array_Data.append(float_row[(init_col-1):])
        Array_Data = np.array(Array_Data)
        Array_Data = Array_Data.T
        return Array_Data, Header

class import_datavalues():
    def __init__(self,FileName):
        data,Header = reading_csv(FileName).read()
        self.DataValue = data[0]
        self.LocalDateTime = data[1]
        self.UTCOffset = data[2]
        self.SiteCode = data[3]
        self.VariableCode = data[4]
        self.CensorCode = data[5]
        self.SourceID = data[6]
        self.QualityControlLevelID = data[7]
        self.MethodDesciption = data[8]
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        (self.connection).commit()
        self.cursor = (self.connection).cursor()

    def importdata(self):
        DataValue = self.DataValue
        LocalDateTime = self.LocalDateTime
        UTCOffset = self.UTCOffset
        SiteCode = self.SiteCode
        VariableCode = self.VariableCode
        CensorCode = self.CensorCode
        SourceID = self.SourceID
        QualityControlLevelID = self.QualityControlLevelID
        MethodDesciption = self.MethodDesciption
        
        n = len(DataValue)
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()
        
        
        ## Create SiteCode, SiteID libary 
        
        SiteID_SiteCode_lib = {}
        SiteID_SiteCode = connection.cursor()
        SiteID_SiteCode.execute('SELECT "SiteCode", "SiteID" FROM dbo."Sites"')
        connection.commit()
        SiteID_SiteCode = SiteID_SiteCode.fetchall()

        for element in SiteID_SiteCode:
            SiteID_SiteCode_lib.update({(element[0]).rstrip():element[1]})
        
        ## Create VariableCode, VariableID libary
                              
        VariableID_VariableCode_lib = {}
        VariableID_VariableCode = connection.cursor()
        VariableID_VariableCode.execute('SELECT "VariableCode", "VariableID" FROM dbo."Variables"')
        connection.commit()
        VariableID_VariableCode = VariableID_VariableCode.fetchall()
        
        for element in VariableID_VariableCode:
            VariableID_VariableCode_lib.update({(element[0]).rstrip():element[1]})

        ## Create MethodID, MethodDesciption
        MethodDesciption_MethodID_lib = {}
        MethodDesciption_MethodID = connection.cursor()
        MethodDesciption_MethodID.execute('SELECT "MethodDescription", "MethodID" FROM dbo."Methods" ')
        MethodDesciption_MethodID = MethodDesciption_MethodID.fetchall()
        for element in MethodDesciption_MethodID:
            MethodDesciption_MethodID_lib.update({(element[0]).rstrip():element[1]})
                

        ## Get UTC_Offset

        UTC_OFFSET_TIMEDELTA = datetime.utcnow() - datetime.now()
        
        ## Note that:
        ## datetime.strptime is a function used to convert  string to datetime type
        ## .strftime is a method used to convert datetime type to string
        
        
        
        ## Set sequence 
        set_seq_cursor = self.cursor
        datavalue_seq = "SELECT setval('dbo." + '"DataValues_ValueID_seq"' + "', (SELECT MAX(" + '"ValueID"'+ ") from dbo." + '"DataValues"'+ "))"
        seriescatalog_seq = "SELECT setval('dbo." + '"SeriesCatalog_SeriesID_seq"' + "', (SELECT MAX(" + '"ValueID"'+ ") from dbo." + '"SeriesID"'+ "))"
        set_seq_cursor.execute(datavalue_seq)
        connection.commit()
        set_seq_cursor.execute(datavalue_seq)
        connection.commit()
        
        
        for i in range(n):
            
            try:
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."DataValues" ("DataValue","LocalDateTime","UTCOffset","DateTimeUTC","SiteID","VariableID","CensorCode","MethodID","SourceID","QualityControlLevelID") VALUES ('\
                        + str(DataValue[i]) +","\
                        + "'" + (datetime.strptime(LocalDateTime[i],"%m/%d/%Y %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S") + "'" + ","\
                        + str(UTCOffset[i]) + ","\
                        + "'" + ((datetime.strptime(LocalDateTime[i],"%m/%d/%Y %H:%M:%S")) + UTC_OFFSET_TIMEDELTA).strftime("%Y-%m-%d %H:%M:%S") + "'"+ ","\
                        + str(SiteID_SiteCode_lib[SiteCode[i]]) + ","\
                        + str(VariableID_VariableCode_lib[VariableCode[i]]) + ","\
                        + "'" +CensorCode[i] + "'" + ","\
                        + str(MethodDesciption_MethodID_lib[MethodDesciption[i]]) + ","\
                        + str(SourceID[i]) + ","\
                        + str(QualityControlLevelID[i])\
                        +')'
                print insert_str
                insert_data.execute(insert_str)
                connection.commit()
                
                
            except:
                if float(DataValue[i]) == -9999:
                    print "Duplicated data"
                else:
                    connection.rollback()
                    update_data = connection.cursor()
                    update_str = 'UPDATE dbo."DataValues" SET "DataValue" = ' + str(DataValue[i]) + ' WHERE '\
                                + '"LocalDateTime" = ' + "'" + (datetime.strptime(LocalDateTime[i],"%m/%d/%Y %H:%M:%S")).strftime("%Y-%m-%d %H:%M:%S") + "'" + " AND "\
                                + '"UTCOffset" = ' + str(UTCOffset[i]) + " AND "\
                                + '"DateTimeUTC" = ' +"'" + ((datetime.strptime(LocalDateTime[i],"%m/%d/%Y %H:%M:%S")) + UTC_OFFSET_TIMEDELTA).strftime("%Y-%m-%d %H:%M:%S") + "'"+ " AND "\
                                + '"SiteID" = ' + str(SiteID_SiteCode_lib[SiteCode[i]]) + " AND "\
                                + '"VariableID" = ' + str(VariableID_VariableCode_lib[VariableCode[i]]) + " AND "\
                                + '"CensorCode" = ' + "'" +CensorCode[i] + "'" + " AND "\
                                + '"MethodID" = ' + str(MethodDesciption_MethodID_lib[MethodDesciption[i]]) + " AND "\
                                + '"SourceID" = ' + str(SourceID[i]) + " AND "\
                                + '"QualityControlLevelID" = ' + str(QualityControlLevelID[i])
                    
                    print update_str
                    update_data.execute(update_str)
                    connection.commit()
        
            ## insert data and update data into series catalog
            
        df = pandas.DataFrame({"id_code":SiteCode,"variable_code":VariableCode,"method_code":MethodDesciption,"source_code":SourceID,"qualitycontrollevel_code":QualityControlLevelID})
        index = (df.groupby(["id_code","variable_code","method_code","source_code","qualitycontrollevel_code"]).size()).reset_index()
        n = len(index.id_code)
        
        
        for i in range(n):
            connection.rollback()
            datetime_data = connection.cursor()
            datetime_str = 'SELECT "LocalDateTime", "DateTimeUTC"'\
                           + ' FROM dbo."DataValues"'\
                           + ' WHERE '+ '"SiteID" = ' + str(format_data(SiteID_SiteCode_lib[(index.id_code)[i]]))  + " AND "\
                           + '"VariableID" =' + str(format_data(VariableID_VariableCode_lib[(index.variable_code)[i]])) + ' ORDER BY "LocalDateTime"'
            datetime_data.execute(datetime_str)
            connection.commit()
            datetime_data = datetime_data.fetchall()
            try:
                print "A"
                update_data = connection.cursor()
                update_str = 'UPDATE dbo."SeriesCatalog" SET "BeginDateTime" = ' + format_data(str(datetime_data[0][0])) + ","\
                            + '"EndDateTime" = ' + format_data(str(datetime_data[0][-1])) + ","\
                            + '"BeginDateTimeUTC" = ' + format_data(str(datetime_data[1][0])) + ","\
                            + '"EndDateTimeUTC" = ' + format_data(str(datetime_data[1][-1]))\
                            + ' WHERE '+ '"SiteCode" = ' + "'" + (index.id_code)[i]+ "'" + " AND "\
                            + '"VariableCode" ='+ format_data((index.variable_code)[i])
                update_data.execute(update_str)
                connection.commit()
            except:
                print "B"
                connection.rollback()
                
                
                ## Get sites data
                sites_data = connection.cursor()
                sites_str = 'SELECT "SiteID", "SiteCode","SiteName","SiteType"'\
                           + ' FROM dbo."Sites"'\
                           + ' WHERE '+ '"SiteID" = ' + str(format_data(SiteID_SiteCode_lib[(index.id_code)[i]]))
                          
                sites_data.execute(sites_str)
                connection.commit()
                sites_data = sites_data.fetchall()


                
                ## Get varibles data
                variables_data = connection.cursor()
                variables_str = 'SELECT "VariableID", "VariableCode","VariableName","Speciation","VariableUnitsID",'\
                                +'"SampleMedium","ValueType","TimeSupport","TimeUnitsID","DataType","GeneralCategory"'\
                           + ' FROM dbo."Variables"'\
                           + ' WHERE '+ '"VariableID" =' + str(format_data(VariableID_VariableCode_lib[(index.variable_code)[i]]))
                variables_data.execute(variables_str)
                connection.commit()
                variables_data = variables_data.fetchall() 

##                ## Get unit data 
                unit_data = connection.cursor()
                unit_str = 'SELECT "UnitsID", "UnitsName"'\
                           + ' FROM dbo."Units"'\
                           + ' WHERE '+ '"UnitsID" =' + str(variables_data[0][4]) + ' OR "UnitsID" = ' + str(variables_data[0][8])          
                unit_data.execute(unit_str)
                connection.commit()
                unit_data = unit_data.fetchall() 
                
                unitid_unitname_lib = {}
                
                for element in unit_data:
                    unitid_unitname_lib.update({(element[0]):element[1].rstrip()})


           
                ## Get method data

                
                method_data = connection.cursor()
                method_str = 'SELECT "MethodID", "MethodDescription"'\
                           + ' FROM dbo."Methods"'\
                           + ' WHERE '+ '"MethodDescription" = ' + format_data(str((index.method_code)[i]))
                print method_str
                method_data.execute(method_str)
                connection.commit()
                method_data = method_data.fetchall() 
                print method_data[0][0]
##                ## Get source data
                source_data = connection.cursor()
                source_str = 'SELECT "SourceID", "Organization","SourceDescription","Citation"'\
                           + ' FROM dbo."Sources"'\
                           + ' WHERE '+ '"SourceID" =' + str((index.source_code)[i])
                source_data.execute(source_str)
                connection.commit()
                source_data = source_data.fetchall() 

               
                ## Get quality control level
                
                qualitycontrollevel_data = connection.cursor()
                qualitycontrollevel_str = 'SELECT "QualityControlLevelID", "QualityControlLevelCode"'\
                           + ' FROM dbo."QualityControlLevels"'\
                           + ' WHERE '+ '"QualityControlLevelID" =' + str((index.qualitycontrollevel_code)[i])
                qualitycontrollevel_data.execute(qualitycontrollevel_str)
                connection.commit()
                qualitycontrollevel_data = qualitycontrollevel_data.fetchall()
        

                
                
               ## Insert data into serierscatalog
                print sites_data[0][3]
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."SeriesCatalog" ("SiteID","SiteCode","SiteName","SiteType",'\
                              +'"VariableID","VariableCode","VariableName","Speciation","VariableUnitsID","VariableUnitsName",'\
                              +'"SampleMedium","ValueType","TimeSupport","TimeUnitsID","TimeUnitsName",'\
                              +'"DataType","GeneralCategory",'\
                              +'"MethodID","MethodDescription",'\
                              +'"SourceID","Organization","SourceDescription","Citation",'\
                              +'"QualityControlLevelID","QualityControlLevelCode",'\
                              +'"BeginDateTime","EndDateTime","BeginDateTimeUTC","EndDateTimeUTC","ValueCount") VALUES ('\
                              + format_data(sites_data[0][0]) +","\
                              + "'" + format_data(sites_data[0][1].rstrip()) + "'" +","\
                              + format_data(sites_data[0][2].rstrip()) +","\
                              + format_data(sites_data[0][3]) +","\
                              + format_data(variables_data[0][0]) +","\
                              + format_data(variables_data[0][1].rstrip()) +","\
                              + format_data(variables_data[0][2].rstrip()) +","\
                              + format_data(variables_data[0][3].rstrip()) +","\
                              + format_data(variables_data[0][4]) +","\
                              + format_data(unitid_unitname_lib[variables_data[0][4]].rstrip()) +","\
                              + format_data(variables_data[0][5].rstrip()) +","\
                              + format_data(variables_data[0][6].rstrip()) +","\
                              + format_data(int(variables_data[0][7])) +","\
                              + format_data(variables_data[0][8]) +","\
                              + format_data(unitid_unitname_lib[variables_data[0][8]]) +","\
                              + format_data(variables_data[0][9].rstrip()) +","\
                              + format_data(variables_data[0][10].rstrip()) +","\
                              + format_data(method_data[0][0]) +","\
                              + format_data(method_data[0][1].rstrip()) +","\
                              + format_data(source_data[0][0]) +","\
                              + format_data(source_data[0][1].rstrip()) +","\
                              + format_data(source_data[0][2].rstrip()) +","\
                              + format_data(source_data[0][3].rstrip()) +","\
                              + format_data(qualitycontrollevel_data[0][0]) +","\
                              + format_data(qualitycontrollevel_data[0][1].rstrip()) +","\
                              + format_data(str(datetime_data[0][0])) + ","\
                              + format_data(str(datetime_data[0][-1])) + ","\
                              + format_data(str(datetime_data[1][0])) + ","\
                              + format_data(str(datetime_data[1][-1])) + ","\
                              + format_data(len(datetime_data[0]))+')'
                print insert_str
                  
                insert_data.execute(insert_str)
                
                connection.commit()
                            
class import_methods():
    def __init__(self,FileName):
        data, Header = reading_csv(FileName).read()
        self.MethodDescription = data[0]
        self.MethodLink = data[1]
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        (self.connection).commit()
        self.cursor = (self.connection).cursor()
    def importdata(self):
        MethodDescription = self.MethodDescription
        MethodLink = self.MethodLink        
        n = len(MethodDescription)
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()

        
        
        ## Set sequence 
        set_seq_cursor = self.cursor
        method_seq = "SELECT setval('dbo." + '"Methods_MethodID_seq"' + "', (SELECT MAX(" + '"MethodID"'+ ") from dbo." + '"Methods"'+ "))"
        set_seq_cursor.execute(method_seq)
        connection.commit()

        
        
        
        for i in range(n):
            try:
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."Methods" ("MethodDescription","MethodLink") VALUES ('\
                        + str(format_data(MethodDescription[i])) +","\
                        + str(format_data(MethodLink[i]))+')'
                print insert_str
                insert_data.execute(insert_str)
                
                connection.commit()
                print insert_str
            except:
                raise "failed"

            
class import_sources():
    def __init__(self,FileName):
        data, Header = reading_csv(FileName).read()
        self.Organization = data[0]
        self.SourceDescription = data[1]
        self.SourceLink = data[2]
        self.ContactName = data[3]
        self.Phone = data[4]
        self.Email = data[5]
        self.Address = data[6]
        self.City = data[7]
        self.SourceState = data[8]
        self.ZipCode = data[9]
        self.Citation = data[10]
        self.MetadataID = data[11]
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        (self.connection).commit()
        self.cursor = (self.connection).cursor()
        
    def importdata(self):
        Organization = self.Organization 
        SourceDescription = self.SourceDescription
        SourceLink = self.SourceLink
        ContactName = self.ContactName
        Phone = self.Phone
        Email = self.Email
        Address = self.Address
        City = self.City
        SourceState = self.SourceState
        ZipCode = self.ZipCode
        Citation  = self.Citation
        MetadataID = self.MetadataID
        
        n = len(Organization )
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()

        
        
        ## Set sequence 
        set_seq_cursor = self.cursor
        source_seq = "SELECT setval('dbo." + '"Sources_SourceID_seq"' + "', (SELECT MAX(" + '"SourceID"'+ ") from dbo." + '"Sources"'+ "))"
        set_seq_cursor.execute(source_seq)
        connection.commit()
        
        
        for i in range(n):
            try:
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."Sources" ("Organization","SourceDescription","SourceLink","ContactName","Phone","Email","Address","City","State","ZipCode","Citation","MetadataID") VALUES ('\
                        + format_data(Organization[i]) + ","\
                        + format_data(SourceDescription[i]) + ","\
                        + format_data(SourceLink[i]) + ","\
                        + format_data(ContactName[i]) + ","\
                        + format_data(Phone[i]) + ","\
                        + format_data(Email[i]) + ","\
                        + format_data(Address[i]) + ","\
                        + format_data(City[i]) + ","\
                        + format_data(SourceState[i]) + ","\
                        + "'" + format_data(ZipCode[i]) + "'" + ","\
                        + format_data(Citation[i]) + ","\
                        + format_data(MetadataID[i]) + ')'
                print insert_str
                insert_data.execute(insert_str)
                connection.commit()
            except:
                raise "Failed"

class import_variables():
    def __init__(self,FileName):
        data, Header = reading_csv(FileName).read()
        self.VariableCode = data[0]
        self.VariableName = data[1]
        self.Speciation = data[2]
        self.VariableUnitsName = data[3]
        self.SampleMedium = data[4]
        self.ValueType = data[5]
        self.IsRegular = data[6]
        self.TimeSupport = data[7]
        self.TimeUnitsName = data[8]
        self.DataType = data[9]
        self.GeneralCategory = data[10]
        self.NoDataValue = data[11]
        
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        (self.connection).commit()
        self.cursor = (self.connection).cursor()
        
    def importdata(self):
        VariableCode = self.VariableCode
        VariableName = self.VariableName
        Speciation = self.Speciation
        VariableUnitsName = self.VariableUnitsName
        SampleMedium = self.SampleMedium
        ValueType = self.ValueType
        IsRegular = self.IsRegular
        TimeSupport = self.TimeSupport
        TimeUnitsName = self.TimeUnitsName
        DataType = self.DataType
        GeneralCategory = self.GeneralCategory
        NoDataValue = self.NoDataValue
        
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        connection.commit()


        ## Create VariableUnitsName - VariableUnitsID lib
        VariableUnitsID_VariableUnitsName_lib = {}
        VariableUnitsID_VariableUnitsName = connection.cursor()
        VariableUnitsID_VariableUnitsName.execute('SELECT "UnitsName", "UnitsID" FROM dbo."Units"')
        connection.commit()
        VariableUnitsID_VariableUnitsName = VariableUnitsID_VariableUnitsName.fetchall()

        for element in VariableUnitsID_VariableUnitsName:
            VariableUnitsID_VariableUnitsName_lib.update({(element[0]).rstrip():element[1]})
            
        
        
        
        ## Set sequence 
        set_seq_cursor = self.cursor
        varible_seq = "SELECT setval('dbo." + '"Variables_VariableID_seq"' + "', (SELECT MAX(" + '"VariableID"'+ ") from dbo." + '"Variables"'+ "))"
        set_seq_cursor.execute(varible_seq)
        connection.commit()
        
        
        
        n = len(VariableCode)
        for i in range(n):
            try:
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."Variables" ("VariableCode","VariableName","Speciation","VariableUnitsID","SampleMedium","ValueType","IsRegular","TimeSupport","TimeUnitsID","DataType","GeneralCategory","NoDataValue") VALUES ('\
                        +  format_data(VariableCode[i]) +","\
                        +  format_data(VariableName[i]) +","\
                        +  format_data(Speciation[i]) +","\
                        +  str(format_data(VariableUnitsID_VariableUnitsName_lib[VariableUnitsName[i]])) + ","\
                        +  format_data(SampleMedium[i]) +","\
                        +  format_data(ValueType[i]) +","\
                        +  format_data(IsRegular[i]) +","\
                        +  format_data(TimeSupport[i]) +","\
                        +  str(format_data(VariableUnitsID_VariableUnitsName_lib[TimeUnitsName[i]])) +","\
                        +  format_data(DataType[i]) +","\
                        +  format_data(GeneralCategory[i]) +","\
                        +  format_data(NoDataValue[i])+')'
                print insert_str
                insert_data.execute(insert_str)
                connection.commit()
                
            except:
                raise "Failed"
                
                
                
class import_sites():
    def __init__(self,FileName):
        data, Header = reading_csv(FileName).read()
        self.SiteCode = data[0]
        self.SiteName = data[1]
        self.Latitude = data[2]
        self.Longitude = data[3]
        self.LatLongDatumSRSName = data[4]
        self.Elevation_m = data[5]
        self.VerticalDatum = data[6]
        self.LocalX = data[7]
        self.LocalY = data[8]
        self.LocalProjectionSRSName = data[9]
        self.PosAccuracy_m = data[10]
        self.State = data[11]
        self.County = data[12]
        self.Comments = data[13]
        
        self.connection = psycopg2.connect(dbname=dbname, user=user, password=password, host = host, port = port)
        (self.connection).commit()
        self.cursor = (self.connection).cursor()
    def importdata(self):
        SiteCode = self.SiteCode
        SiteName = self.SiteName
        Latitude = self.Latitude
        Longitude = self.Longitude
        LatLongDatumSRSName = self.LatLongDatumSRSName
        Elevation_m = self.Elevation_m
        VerticalDatum = self.VerticalDatum
        LocalX = self.LocalX
        LocalY = self.LocalY
        LocalProjectionSRSName = self.LocalProjectionSRSName
        PosAccuracy_m = self.PosAccuracy_m
        State = self.State
        County = self.County
        Comments = self.Comments
        n = len(SiteCode)
        connection = self.connection
        connection.commit()

        ## Create VariableUnitsName - VariableUnitsID lib
        ProjectionID_ProjectionName_lib = {}
        ProjectionID_ProjectionName = connection.cursor()
        ProjectionID_ProjectionName.execute('SELECT "SRSName","SpatialReferenceID" FROM dbo."SpatialReferences"')
        connection.commit()
        ProjectionID_ProjectionName = ProjectionID_ProjectionName.fetchall()

        for element in ProjectionID_ProjectionName:
            ProjectionID_ProjectionName_lib.update({(element[0]).rstrip():element[1]})
        
        
        
        ## Set sequence 
        set_seq_cursor = self.cursor
        dbo_site_seq = "SELECT setval('dbo." + '"Sites_SiteID_seq"' + "', (SELECT MAX(" + '"SiteID"'+ ") from dbo." + '"Sites"'+ "))"
        set_seq_cursor.execute(dbo_site_seq)
        connection.commit()
        
        public_site_seq = "SELECT setval('public." + 'gis_apps_stations' + "', (SELECT MAX(" + '"id"'+ ") from public." + '"gis_apps_stations"'+ "))"
        
        
        for i in range(n):
            try:
                
                
                insert_data = connection.cursor()
                insert_str = 'INSERT INTO dbo."Sites" ("SiteCode","SiteName","Latitude","Longitude","LatLongDatumID","Elevation_m" ,"VerticalDatum","LocalX","LocalY","LocalProjectionID","PosAccuracy_m","State","County","Comments") VALUES ('\
                                                        + "'"+ format_data(SiteCode[i])+"'" +","\
                                                        + format_data(SiteName[i]) + ","\
                                                        + format_data(Latitude[i]) +","\
                                                        + format_data(Longitude[i]) + ","\
                                                        + str(format_data(ProjectionID_ProjectionName_lib[LatLongDatumSRSName[i]])) + ","\
                                                        + format_data(Elevation_m[i]) +","\
                                                        + format_data(VerticalDatum[i]) + ","\
                                                        + format_data(LocalX[i]) + ","\
                                                        + format_data(LocalY[i]) + ","\
                                                        + str(format_data(ProjectionID_ProjectionName_lib[LocalProjectionSRSName[i]])) +","\
                                                        + format_data(PosAccuracy_m[i]) +","\
                                                        + format_data(State[i]) + ","\
                                                        + format_data(County[i]) + ","\
                                                        + format_data(Comments[i])  + ')'
                
                print insert_str

                insert_data.execute(insert_str)     
                connection.commit()        

            
            
            
            except:
                print "failed"

                
## import in to postgis
        for i in range(n):
            try:
##                pointX = -105.150271116 
##                pointY = 39.7278572773

                # Spatial Reference System
                inputEPSG = 4326
                outputEPSG = 3857

                # create a geometry from coordinates
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(float(Longitude[i]),float(Latitude[i]))

                # create coordinate transformation
                inSpatialRef = osr.SpatialReference()
                inSpatialRef.ImportFromEPSG(inputEPSG)

                outSpatialRef = osr.SpatialReference()
                outSpatialRef.ImportFromEPSG(outputEPSG)

                coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

                # transform point
                point.Transform(coordTransform)

                # print point in EPSG 3857
                
                
                geometry = "ST_GeomFromText('MULTIPOINT(%s %s)',3857)"%(str(point.GetX()),str(point.GetY()))
                
                
                insert_data = connection.cursor()
                insert_str = "INSERT INTO gis_apps_stations(name,sitecode,geometry) VALUES("\
                                + format_data(SiteName[i]) + ","\
                                + "'"+ format_data(SiteCode[i])+"'" +","\
                                + geometry + ")"
                insert_data.execute(insert_str)
                connection.commit()
            except:
                raise "failed"                
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################


dbname = "dss2"
user = "postgres"
host = "localhost"
port = "5432"
password =""


# Get dir path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_DIR = os.path.join(BASE_DIR, 'media/uploaded_file')


def upload(request):
    return render_to_response('uploadfile.html')



@csrf_exempt
def confirm_upload(request):
    if request.method == 'POST':
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            args = {}
            args.update(csrf(request))
            filename = ((request.FILES['upload_file']).name).replace(".csv","")
            return render_to_response('import_'+filename+'.html',args)
    else:
        form = UploadForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    
    filename = (request.FILES['filename']).name
    
    return render_to_response('uploadfile.html',args)

def save_methods(request):
    (import_methods(FILE_DIR+'/methods.csv')).importdata()
    os.remove(FILE_DIR+'/methods.csv')
    return render_to_response('importseriesdata.html')
    
def save_sources(request):
    (import_sources(FILE_DIR+'/sources.csv')).importdata()
    os.remove(FILE_DIR+'/sources.csv')
    return render_to_response('importseriesdata.html')

def save_variables(request):
    (import_variables(FILE_DIR+'/variables.csv')).importdata()
    os.remove(FILE_DIR+'/variables.csv')
    return render_to_response('importseriesdata.html')

def save_sites(request):
    (import_sites(FILE_DIR+'/sites.csv')).importdata()
    os.remove(FILE_DIR+'/sites.csv')
    return render_to_response('importseriesdata.html')

def save_datavalues(request):
    (import_datavalues(FILE_DIR+'/datavalues.csv')).importdata()
    os.remove(FILE_DIR+'/datavalues.csv')
    return render_to_response('importseriesdata.html')

