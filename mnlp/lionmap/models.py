from django.contrib.gis.db import models
from singleton_models.models import SingletonModel


class Lion(models.Model):
    SEX_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Unknown'),
    )

    name = models.CharField(max_length=25, unique=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, )
    age = models.IntegerField()
    ageDate = models.DateField()
    pride = models.ForeignKey('Pride')
    collars = models.ManyToManyField('Collar', through='Tracking', blank=True,
        null=True)

    objects = models.GeoManager()  # relation to model with geo data

    def __unicode__(self):
        return self.name


class Collar(models.Model):
    serial = models.CharField(max_length=25)

    objects = models.GeoManager()  # relation to model with geo data

    def __unicode__(self):
        return self.serial


class Position(models.Model):
    collar = models.ForeignKey('Collar')
    timestamp = models.DateTimeField()
    coordinate = models.PointField(geography=True)  # default SRID = EPSG:4326 aka WGS84
    altitude = models.FloatField()

    objects = models.GeoManager()

    def __unicode__(self):
        return str(self.collar) + "|" + str(self.timestamp)


class Pride(models.Model):
    name = models.CharField(max_length=25)

    objects = models.GeoManager()

    def __unicode__(self):
        return self.name


class Tracking(models.Model):
    lion = models.ForeignKey('Lion')
    collar = models.ForeignKey('Collar')
    start = models.DateTimeField()
    end = models.DateTimeField()

    objects = models.GeoManager()

    def __unicode__(self):
        return "%s / %s [%s-%s]" % (self.lion.name, self.collar.serial, self.start, self.end)


class DropboxAccount(SingletonModel):
    name = models.CharField(max_length=50)
    key = models.CharField(max_length=15, blank=True)
    secret = models.CharField(max_length=15, blank=True)
    delta = models.CharField(max_length=80, blank=True)

    def dropbox_link(self):
        return reverse('admin_lionmap_dropboxaccount_link')

    class Meta:
        verbose_name = "Dropbox Account"  # once again this will make sure your admin UI doesn't have illogical text
        verbose_name_plural = "Dropbox Account"

    def __unicode__(self):
        return self.name
