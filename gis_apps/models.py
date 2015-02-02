from django.db import models
from django.contrib.gis.db import models
# Create your models here.

class province_boundary(models.Model):
    province = models.CharField(max_length=254)
    population = models.FloatField(null=True)
    area = models.FloatField(null=True)
    objects = models.GeoManager()
    geometry = models.MultiPolygonField(srid =3857)
    def __str__(self):
        return self.province

    
class stations(models.Model):
    name = models.CharField(max_length=254)
    sitecode = models.CharField(max_length=254)
    objects = models.GeoManager()
    geometry = models.MultiPointField(srid =3857)
    def __str__(self):
        return self.name
 





class landuse(models.Model):
    code = models.CharField(max_length=3)
    description = models.CharField(max_length=255,null=True)
    objects = models.GeoManager()
    geometry = models.MultiPolygonField(srid =3857)
    def __str__(self):
        return self.code
    