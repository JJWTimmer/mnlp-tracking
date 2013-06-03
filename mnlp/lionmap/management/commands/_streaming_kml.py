import re
import datetime
import zipfile
import os

from lxml import etree
from django.core.exceptions import ObjectDoesNotExist

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
                    print "Error unzipping: %s" % err
                    return
            else:
                print "not zip or no doc.kml"
        except Exception, e:
            print "error checking if zip: %s" % e
            return

    def parse_positions(self):
        doc_context = etree.iterparse(self.filename, events=('end',), tag='{http://earth.google.com/kml/2.2}Document', encoding='utf-8')
        context = etree.iterparse(self.filename, events=('end',), tag='Placemark', encoding='utf-8')

        collarname = None
        xp = etree.XPath("//*[local-name()='name']/text()")
        for action, elem in doc_context:
            collarname = xp(elem)[0]
            break

        if not collarname:
            print "no collarname found"
            return

        try:
            collar = Collar.objects.get(serial=collarname)
        except ObjectDoesNotExist:
            collar = Collar.objects.create(serial=collarname)
            collar.save()
        except Exception, e:
            print "db error: %s" % e

        try:
            fast_iter(context, lambda elem: make_fix(elem, collar))
        except Exception, e:
            print "error iterating: %s" % e
        finally:
            if self.delete_zip:
                os.unlink("~/volatile/doc.kml")

def fast_iter(context, func):
    for event, elem in context:
        func(elem)
        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    del context


def make_fix(elem, collar):
    xp1 = etree.XPath("//name/text()")
    xp2 = etree.XPath("//Timestamp/when/text()")
    xp3 = etree.XPath("//Point//coordinates/text()")
    xp4 = etree.XPath("//description/text()")

    fix = Fix(xp1(elem)[0], xp2(elem)[0], xp3(elem)[0], xp4(elem)[0])
    if fix.valid:
        #if the fix already exists, don't create it again
        try:
            position = Position.objects.get(collar=collar, timestamp=fix.timestamp)
        except ObjectDoesNotExist:
            position = Position.objects.create(collar=collar, timestamp=fix.timestamp, coordinate="POINT(%s %s)" % (fix.latitude, fix.longitude), altitude=fix.altitude)
            position.save()


class Fix(object):
    def __init__(self, num, timestamp, coordinates, description):
        self.number = int(re.search(r"Fix #(\d+)", num).group(1))
        self.timestamp = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
        self.timestamp = self.timestamp.replace(tzinfo=pytz.timezone("UTC"))
        lat, lon, alt = coordinates.split(', ')
        self.coordinates = coordinates
        self.longitude = float(lon)
        self.latitude = float(lat)
        self.altitude = float(alt)
        self.valid = False if 'not val.' in description else True