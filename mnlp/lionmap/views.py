from django.template import Context, loader
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.gis.shortcuts import render_to_kml
from lionmap.models import Lion, Position
from lionmap.forms import DateFilterForm
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.conf import settings

def kml(request, lion):
    dayago = datetime.now() - timedelta(days=1)
    eightdaysago = datetime.now() - timedelta(days=8)

    lowerbound = request.session['kml_start'] if 'kml_start' in request.session else eightdaysago
    upperbound = request.session['kml_end'] if 'kml_end' in request.session else dayago

    positions = Position.objects.filter(
        collar__lion__pk=int(lion),
        collar__tracking__start__lte=datetime.now(),
        collar__tracking__end__gte=datetime.now(),
        timestamp__gte=lowerbound,
        timestamp__lte=upperbound
    ).kml()

    return render_to_kml("gis/placemarks.kml", {"places": positions})


def map(request):
    if request.method == 'POST':
        form = DateFilterForm(request.POST)
        if form.is_valid():
            request.session['kml_start'] = form.cleaned_data['start']
            request.session['kml_end'] = form.cleaned_data['end']
    else:
        form = DateFilterForm()

    return render(request, "map.html", {'form': form})

def fullscreen(request):
    return render_to_response("fullscreen.html")

def lions(request):
    lions = Lion.objects.all()
    lionlist = []
    for lion in lions:
        liondict = {}
        liondict['id'] = lion.id
        liondict['name'] = lion.name
        lionlist.append(liondict)
    response_data = { 'lions': lionlist }
    return HttpResponse(simplejson.dumps(response_data), mimetype="application/json")

@login_required
def last_positions(request):
    positions = []
    try:
        lions = Lion.objects.all()

        for lion in lions:
            last_pos = Position.objects.filter(
                collar__lion__pk=lion.pk,
                collar__tracking__start__lte=datetime.now(),
                collar__tracking__end__gte=datetime.now()
            ).latest('timestamp')

            positions.append( (lion.name, Position.objects.filter(pk=last_pos.pk).get().timestamp, Position.objects.filter(pk=last_pos.pk).kml()) )
    except Exception, err:
        print err

    return render_to_kml("gis/lions.kml", {"lions": positions})

@login_required
def retrieve_heatmap(request, file_name):
    response = HttpResponse() # 200 OK
    del response['content-type'] # We'll let the web server guess this.
    response['X-Accel-Redirect'] = '/static/heatmaps/' + file_name
    return response