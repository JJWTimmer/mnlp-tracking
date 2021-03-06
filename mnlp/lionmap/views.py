from datetime import datetime, timedelta
import json

from django.http import HttpResponse

from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.db.models import F

from lionmap.models import Lion, Position

from lionmap.forms import DateFilterForm


def get_positions(request, lion):
    threedaysago = datetime.now() - timedelta(days=3)
    tendaysago = datetime.now() - timedelta(days=10)

    lowerbound = datetime.strptime(request.session['kml_start'],
                                   "%Y-%m-%d").date() if 'kml_start' in request.session else tendaysago
    upperbound = datetime.strptime(request.session['kml_end'],
                                   "%Y-%m-%d").date() if 'kml_end' in request.session else threedaysago

    return Position.objects.filter(
        collar__tracking__lion__pk=int(lion),
        collar__tracking__start__lte=upperbound,
        collar__tracking__end__gte=lowerbound,
        timestamp__range=(lowerbound, upperbound)
    ).filter(
        timestamp__gte=F('collar__tracking__start'),
        timestamp__lte=F('collar__tracking__end')
    )


def get_lions_in_range(request):
    threedaysago = datetime.now() - timedelta(days=3)
    tendaysago = datetime.now() - timedelta(days=10)

    lowerbound = datetime.strptime(request.session['kml_start'],
                                   "%Y-%m-%d").date() if 'kml_start' in request.session else tendaysago
    upperbound = datetime.strptime(request.session['kml_end'],
                                   "%Y-%m-%d").date() if 'kml_end' in request.session else threedaysago

    return Position.objects.filter(
        collar__tracking__start__lte=upperbound,
        collar__tracking__end__gte=lowerbound,
        timestamp__range=(lowerbound, upperbound)
    ).values('collar__tracking__lion__pk').distinct()


def positions_to_json(request, lion):
    positions = [{'lat': pos.coordinate.y, 'lon': pos.coordinate.x, 'count': 1} for pos in get_positions(request, lion)]
    response_data = {'max': 10, 'data': positions}
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def lion_data(request):
    lions = get_lions_in_range(request)

    positions = {}
    for lion_dict in lions.iterator():
        lion = Lion.objects.get(id=lion_dict['collar__tracking__lion__pk'])
        positions[lion.name] = [{'lat': pos.coordinate.y, 'lon': pos.coordinate.x, 'timestamp': pos.timestamp} for pos
                                in get_positions(request, lion.id)]

    geojson = {}
    geojson['type'] = 'FeatureCollection'
    geojson['features'] = [
        {'type': 'Feature',
         'geometry': {
             'type': 'GeometryCollection',
             'geometries': [
                 {
                     'type': 'Point',
                     'coordinates': [
                         coords['lon'],
                         coords['lat']

                     ],
                     'properties': {
                         'timestamp': str(coords['timestamp'])
                     }
                 }
                 for coords in positions[name]
             ]
         },
         'properties': {
             'lion': name
         }
        }

        for name in positions.iterkeys()
    ]

    return HttpResponse(json.dumps(geojson), content_type='application/json')


def heatmap_data(request):
    lions = get_lions_in_range(request)

    positions = []
    for lion_dict in lions.iterator():
        lion = Lion.objects.get(id=lion_dict['collar__tracking__lion__pk'])
        positions += [{'lat': pos.coordinate.y, 'lon': pos.coordinate.x, 'value': 1} for pos
                      in get_positions(request, lion.id)]

    return HttpResponse(json.dumps(positions, allow_nan=False, indent=2), content_type='application/json')


def kml(request, lion):
    positions = get_positions(request, lion)

    from django.core import serializers

    geojson = serializers.serialize("json", positions)

    return HttpResponse(geojson, mimetype="application/json")


def show_map(request):
    if request.method == 'POST':
        form = DateFilterForm(request.user, request.POST)
        if form.is_valid():
            request.session['kml_start'] = str(form.cleaned_data['start'])
            request.session['kml_end'] = str(form.cleaned_data['end'])
    else:
        form = DateFilterForm(request.user)

    return render(request, "map.html", {'form': form})


def fullscreen(request):
    return render_to_response("fullscreen.html")


def lions(request):
    lions = Lion.objects.all()
    lionlist = []
    for lion in lions:
        liondict = {'id': lion.id, 'name': lion.name}
        lionlist.append(liondict)
    response_data = {'lions': lionlist}
    return HttpResponse(json.dumps(response_data), content_type="application/json")


@login_required
def last_positions(request):
    positions = []
    try:
        lions = Lion.objects.all()

        for lion in lions:
            last_pos = Position.objects.filter(
                collar__tracking__lion__pk=lion.pk
            ).filter(
                timestamp__gte=F('collar__tracking__start'),
                timestamp__lte=F('collar__tracking__end')
            ).latest('timestamp')

            positions.append((lion.name, str(last_pos.timestamp),
                              last_pos.coordinate.tuple))
    except Exception, err:
        print err

    return HttpResponse(json.dumps(positions), content_type="application/json")


try:
    from local_views import *
except ImportError:
    pass
