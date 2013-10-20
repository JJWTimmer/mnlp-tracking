from django.template import Context, loader
from datetime import datetime, timedelta
from django.http import HttpResponse
from django.shortcuts import render_to_response, render
from django.contrib.gis.shortcuts import render_to_kml
from lionmap.models import Lion, Position
from lionmap.forms import DateFilterForm
from django.utils import simplejson
from django.contrib.auth.decorators import login_required
from django.db.models import F
import json


def get_positions(request, lion):
    threedaysago = datetime.now() - timedelta(days=3)
    tendaysago = datetime.now() - timedelta(days=10)

    lowerbound = request.session['kml_start'] if 'kml_start' in request.session else tendaysago
    upperbound = request.session['kml_end'] if 'kml_end' in request.session else threedaysago

    return Position.objects.filter(
            collar__lion__pk=int(lion),
            collar__tracking__lion__pk=int(lion),
            collar__tracking__start__lte=datetime.now(),
            collar__tracking__end__gte=datetime.now(),
            timestamp__range=(lowerbound, upperbound)
        ).filter(
            timestamp__gte=F('collar__tracking__start'),
            timestamp__lte=F('collar__tracking__end')
        )


def positions_to_json(request, lion):
    positions = [{'lat': pos.coordinate.y, 'lon': pos.coordinate.x, 'count': 1} for pos in get_positions(request, lion)]
    response_data = {'max': 10, 'data': positions}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def kml(request, lion):
    positions = get_positions(request, lion).kml()

    return render_to_kml("gis/placemarks.kml", {"places": positions})


def map(request):
    if request.method == 'POST':
        form = DateFilterForm(request.user, request.POST)
        if form.is_valid():
            request.session['kml_start'] = form.cleaned_data['start']
            request.session['kml_end'] = form.cleaned_data['end']
    else:
        form = DateFilterForm(request.user)

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
    response_data = {'lions': lionlist}
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
                collar__tracking__end__gte=datetime.now(),
                timestamp__gte=F('collar__tracking__start'),
                timestamp__lte=F('collar__tracking__end')
            ).latest('timestamp')

            positions.append((lion.name, Position.objects.filter(pk=last_pos.pk).get().timestamp,
                              Position.objects.filter(pk=last_pos.pk).kml()))
    except Exception, err:
        print err

    return render_to_kml("gis/lions.kml", {"lions": positions})


try:
    from local_views import *
except ImportError:
    pass
