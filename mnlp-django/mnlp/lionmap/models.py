from django.contrib.gis.db import models

class Lion(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Unknown'),
    )

    name = models.CharField(max_length=25, unique=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, )
    birthDate = models.DateField()
    
    objects = models.GeoManager() # relation to field with geo data somewhere chained
    
    def __unicode__(self):
        return self.name
        
class Collar(models.Model):
    serial = models.CharField(max_length=25)
    lion = models.OneToOneField('Lion')

    objects = models.GeoManager() #relation to field with geo data
    
    def __unicode__(self):
        return self.serial

class Position(models.Model):
    collar = models.ForeignKey(Collar)
    timestamp = models.DateTimeField()
    coordinate = models.PointField(geography=True) #default SRID = EPSG:4326 aka WGS84
    temperature = models.DecimalField(max_digits=3, decimal_places=1)
    
    objects = models.GeoManager()

    # Returns the string representation of the model.
    def __unicode__(self):
        return str(self.collar) + "|" + str(self.timestamp)