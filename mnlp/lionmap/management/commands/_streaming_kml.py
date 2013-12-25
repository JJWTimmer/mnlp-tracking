import re
import datetime
import zipfile
import os

from lxml import etree
from django.core.exceptions import ObjectDoesNotExist
import pytz

from lionmap.models import Collar
from lionmap.models import Position


class KMZFile(object):
    def __init__(self, filename):
        self.filename = filename
        self.delete_zip = False

        try:
            if zipfile.is_zipfile(filename) and 'doc.kml' in zipfile.namelist():
                try:
                    zipf = zipfile.ZipFile(filename)
                    zipf.extract('doc.kml', '~/volatile')
                    self.filename = "~/volatile/doc.kml"
                    self.delete_zip = True
                except Exception, err:
                    raise Exception("Error unzipping: %s" % err)
            else:
                print "not zip or no doc.kml"
        except Exception, e:
            raise Exception("Error checking if zip: %s" % e)

    def parse_positions(self):
        doc_context = etree.iterparse(self.filename, events=('end',), tag='{http://earth.google.com/kml/2.2}Document',
                                      encoding='utf-8')
        context = etree.iterparse(self.filename, events=('end',), tag='{http://earth.google.com/kml/2.2}Placemark',
                                  encoding='utf-8')

        collarname = None
        xp = etree.XPath("//*[local-name()='name']/text()")
        for action, elem in doc_context:
            collarname_result = xp(elem)
            if len(collarname_result) > 0:
                collarname = collarname_result[0]
                break
            else:
                raise Exception("Error getting collarname")

        if not collarname:
            raise Exception("No collarname found")

        try:
            collar = Collar.objects.get(serial=collarname)
        except ObjectDoesNotExist:
            collar = Collar.objects.create(serial=collarname)
            collar.save()
        except Exception, e:
            raise Exception("DB Error: %s" % e)

        try:
            fast_iter(context, lambda elem: make_fix(elem, collar))
        except Exception, e:
            raise Exception("Error iterating: %s" % e)
        finally:
            if self.delete_zip:
                try:
                    os.unlink("~/volatile/doc.kml")
                except:
                    pass


def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def make_fix(elem, collar):
    xp1 = etree.XPath("./*[local-name()='name']/text()")
    xp2 = etree.XPath("./*[local-name()='TimeStamp']/*[local-name()='when']/text()")
    xp3 = etree.XPath("./*[local-name()='Point']/*[local-name()='coordinates']/text()")
    xp4 = etree.XPath("./*[local-name()='description']/text()")

    num = xp1(elem)
    ts = xp2(elem)
    coords = xp3(elem)
    desc = xp4(elem)

    if not (len(num) > 0 and 'Fix' in num[0]):
        return

    fix = Fix(num[0], ts[0], coords[0], desc[0])
    if fix.valid:
        #if the fix already exists, don't create it again
        try:
            position = Position.objects.get(collar=collar, timestamp=fix.timestamp)
        except ObjectDoesNotExist:
            position = Position.objects.create(collar=collar, timestamp=fix.timestamp,
                                               coordinate="SRID=4326;POINT(%s %s)" % (fix.latitude, fix.longitude),
                                               altitude=fix.altitude)
            position.save()


class Fix(object):
    def __init__(self, num, timestamp, coordinates, description):
        try:
            self.number = int(re.search(r"Fix #(\d+)", num).group(1))
            self.timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
            self.timestamp = self.timestamp.replace(tzinfo=pytz.timezone("UTC"))
            lat, lon, alt = coordinates.split(', ')
            self.coordinates = coordinates
            self.longitude = float(lon)
            self.latitude = float(lat)
            self.altitude = float(alt)
            self.valid = False if 'not val.' in description else True
        except:
            self.valid = False
