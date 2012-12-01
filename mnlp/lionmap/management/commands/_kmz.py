import zipfile, StringIO, datetime, re, tempfile, os
from pykml import parser
from lxml import etree, objectify
from django.core.exceptions import ObjectDoesNotExist
from lionmap.models import Collar, Position
import pytz


class KMZFile(object):
    def __init__(self, file):
        self.valid = False
        tfile = tempfile.NamedTemporaryFile(mode='w', delete=False)
        tfile.write(file)
        tfile.close()

        try:
            if zipfile.is_zipfile(tfile.name):
                try:
                    zipf = zipfile.ZipFile(StringIO.StringIO(file))
                    dockml = zipf.open('doc.kml')
                    doc = dockml.read()
                    dockml.close()
                except Exception, err:
                    print "Error unzipping: %s" % err
                    return
            else:
                print "not zip"
                doc = file
        except Exception, e:
            print "error in unpacking file: %s" % e
            return
        finally:
            os.unlink(tfile.name)

        try:
            assert isinstance(doc, str)
            unicode_content = doc.decode('utf-8')
            xml_content = unicode_content.encode('ascii', 'xmlcharrefreplace')
            root = parser.fromstring(xml_content)
        except Exception, e:
            print "error decoding: %s" % e
            return

        self.root = root
        self.xml = xml_content
        self.valid = True

    def save_positions(self):
        try:
            collar = Collar.objects.get(serial=self.root.Document.name.text)
        except ObjectDoesNotExist:
            collar = Collar.objects.create(serial=self.root.Document.name.text)
            collar.save()
        except Exception, e:
            print "db error: %s" % e

        try:
            placemarks = [el for el in self.root.Document.Folder.iterchildren() if el.tag == '{http://earth.google.com/kml/2.2}Placemark']
            for placemark in placemarks:
                try:
                    fix = Fix(placemark.name.text, placemark.TimeStamp.when.text, placemark.Point.coordinates.text, placemark.description.text)

                    if not fix.valid:
                        continue

                    #if the fix already exists, don't create it again
                    try:
                        position = Position.objects.get(collar=collar, timestamp=fix.timestamp)
                    except ObjectDoesNotExist:
                        position = Position.objects.create(collar=collar, timestamp=fix.timestamp, coordinate="POINT(%s %s)" % (fix.latitude, fix.longitude), altitude=fix.altitude)
                        position.save()
                except AttributeError, e2:
                    print "attrib error: %s" % e2
                    return
                except Exception, e3:
                    print "other exception: %s" % e3
                    return
        except Exception, e1:
            print "Loop exception: %s" % e1


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
