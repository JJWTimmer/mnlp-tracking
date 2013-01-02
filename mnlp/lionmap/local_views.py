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

