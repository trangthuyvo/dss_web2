from django.db import models
from time import time


# Create your models here.

def get_upload_file_name(instance,filename):
    return "uploaded_file/%s"%(filename)

class Upload(models.Model):
    upload_file = models.FileField(upload_to = get_upload_file_name)
    def __unicode__(self):
        return self.title