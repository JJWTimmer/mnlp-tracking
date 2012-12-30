import os
from datetime import timedelta, datetime
from django.core.management.base import NoArgsCommand
from django.conf import settings
import heatmap
from lionmap.models import Lion, Position, Tracking, Collar

class Command(NoArgsCommand):
    help = 'Creates heatmaps per lion and for all lions'
    can_import_settings = True

    def handle_noargs(self, **options):
        #try:
            map_dir = os.path.join(settings.STATIC_ROOT, 'heatmaps')

            minx, miny = 35.14455174999947, -1.4807579817798406
            maxx, maxy = 35.496114249999806, -1.3050287418975504

            lions = Lion.objects.filter(
                tracking__start__lte=datetime.now(),
                tracking__end__gte=datetime.now()
            )

            for lion in lions:
                month_positions = Position.objects.filter(
                    collar__lion__pk=lion.pk,
                    collar__tracking__start__lte=datetime.now(),
                    collar__tracking__end__gte=datetime.now(),
                    timestamp__gte=(datetime.now() - timedelta(days=30)),
                    timestamp__lte=datetime.now()
                ).order_by('timestamp')

                if len(month_positions) == 0:
                    last_pos = Position.objects.filter(
                        collar__lion__pk=int(lion),
                        collar__tracking__start__lte=datetime.now(),
                        collar__tracking__end__gte=datetime.now(),
                        timestamp__lte=(datetime.now() - timedelta(days=30)),
                        timestamp__gte=datetime.now()
                    ).latest('timestamp')

                    lowerbound = last_pos.timestamp - timedelta(days=7)

                    month_positions = Position.objects.filter(
                    collar__lion__pk=lion.pk,
                    collar__tracking__start__lte=datetime.now(),
                    collar__tracking__end__gte=datetime.now(),
                    timestamp__lte=(datetime.now() - timedelta(days=30)),
                    timestamp__gte=datetime.now()
                ).order_by('timestamp')

                pts = [(pos.coordinate.x, pos.coordinate.y) for pos in month_positions]

                if not len(pts) == 0:
                    hm = heatmap.Heatmap()
                    hm.heatmap(pts, size=(1024, 512), area=((minx, miny), (maxx, maxy)), dotsize=25)
                    hm.saveKML(os.path.join(map_dir, "%s.kml" % lion.name ))

        #except Exception, err:
            #print err