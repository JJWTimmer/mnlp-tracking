from django.template import Context, loader
from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib.gis.shortcuts import render_to_kml
from lionmap.models import Position

def hello_view(request):
    """ Simple Hello World View """
    t = loader.get_template('helloworld.html')
    c = Context({
        'current_time': datetime.now(),
    })
    return HttpResponse(t.render(c))
    
def kml(request):
    positions = Position.objects.all().kml()
    return render_to_kml("gis/placemarks.kml", {"places" : positions})