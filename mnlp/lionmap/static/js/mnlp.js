var TheMap = {
    data : {
        map : null,
        map2 : null,
        lionLayers : [],
        heatmapLayer : null,
        selectControl : null,
        bounds : null
    },

    init : function() {
        TheMap.data.map = new OpenLayers.Map('map_canvas', {
            controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher({'ascending':false}),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.KeyboardDefaults()
            ]
        });
        var osm = new OpenLayers.Layer.OSM("Open Street Map");

        var gphy = new OpenLayers.Layer.Google(
            "Google Physical",
            {type: google.maps.MapTypeId.TERRAIN}
            // used to be {type: G_PHYSICAL_MAP}
        );
        var gmap = new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
            // default type, no change needed here
        );
        var ghyb = new OpenLayers.Layer.Google(
            "Google Hybrid",
            {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
            // used to be {type: G_HYBRID_MAP, numZoomLevels: 20}
        );
        var gsat = new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
            // used to be {type: G_SATELLITE_MAP, numZoomLevels: 22}
        );

        //TheMap.data.map.addLayer(osm);
        TheMap.data.map.addLayers([osm, gphy, gmap, ghyb, gsat]);

        TheMap.data.bounds = new OpenLayers.Bounds();


        center = TheMap.getLonLat(35.320333, -1.392895);

        zoom = 12;

        TheMap.data.map.setCenter(center, zoom);

        //position color-ramp
        var colors = ['#00FF00', '#0000FF', '#FF0000', '#01FFFE', '#FFA6FE', '#FFDB66', '#006401', '#010067', '#95003A', '#007DB5', '#FF00F6', '#FFEEE8', '#774D00', '#90FB92', '#0076FF', '#D5FF00', '#FF937E', '#6A826C', '#FF029D', '#FE8900', '#7A4782', '#7E2DD2', '#85A900', '#FF0056', '#A42400', '#00AE7E', '#683D3B', '#BDC6FF', '#263400', '#BDD393', '#00B917', '#9E008E', '#001544', '#C28C9F', '#FF74A3', '#01D0FF', '#004754', '#E56FFE', '#788231', '#0E4CA1', '#91D0CB', '#BE9970', '#968AE8', '#BB8800', '#43002C', '#DEFF74', '#00FFC6', '#FFE502', '#620E00', '#008F9C', '#98FF52', '#7544B1', '#B500FF', '#00FF78', '#FF6E41', '#005F39', '#6B6882', '#5FAD4E', '#A75740', '#A5FFD2', '#FFB167', '#009BFF', '#E85EBE'];

        $.getJSON(
            "/lions",
            function(data){
                var size = data['lions'].length;
                for (var i=0; i<size; i++) {

                    var style = new OpenLayers.Style(
                        {
                            pointRadius: "${radius}",
                            fillColor: colors[i],
                            fillOpacity: 0.8,
                            strokeColor: colors[i],
                            strokeWidth: 2,
                            strokeOpacity: 0.8
                        }, {
                            context: {
                                radius: 2,
                            }
                        }
                    );

                    var stylemap = new OpenLayers.StyleMap({
                        "default": style,
                        "select": {
                            fillColor: "#8aeeef",
                            strokeColor: "#32a8a9"
                        }
                    });

                    TheMap.data.lionLayers.push(
                        new OpenLayers.Layer.Vector(
                            data['lions'][i]['name'],
                            {
                                strategies: [new OpenLayers.Strategy.Fixed()],
                                projection: TheMap.data.map.displayProjection,
                                protocol: new OpenLayers.Protocol.HTTP({
                                    url: "/kml/lion/" + data['lions'][i]['id'] + '/',
                                    format: new OpenLayers.Format.KML({
                                        extractStyles: true,
                                        extractAttributes: true
                                    })
                                }),
                                styleMap: stylemap
                            }
                        )
                    );
                };
                TheMap.data.map.addLayers(TheMap.data.lionLayers);
            }
        );
    },

    onFeatureHighlighted: function (evt) {
        // Needed only for interaction, not for the display.
        var onPopupClose = function (evt) {
            // 'this' is the popup.
            var feature = this.feature;
            if (feature.layer) {
                TheMap.data.selectControl.unselect(feature);
            }

            this.destroy();
        }

        var feature = evt.feature;
        var popup = new OpenLayers.Popup.FramedCloud(
            "featurePopup",
            feature.geometry.getBounds().getCenterLonLat(),
            null,
            "<h2>" + feature.data.name + "</h2><p>" + feature.data.description + "</p>",
            null,
            true,
            onPopupClose);
        feature.popup = popup;
        popup.feature = feature;
        TheMap.data.map.addPopup(popup, true);
    },
    onFeatureUnHighlighted: function (evt) {
        for (var i=0; i < TheMap.data.map.popups.length; i++) {
            TheMap.data.map.popups[i].hide();
            TheMap.data.map.popups[i].destroy();

        }
    },

    lastpos : function() {
        TheMap.data.map = new OpenLayers.Map('map_canvas', {
            controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher({'ascending':false}),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.KeyboardDefaults()
            ]
        });
        var osm = new OpenLayers.Layer.OSM("Open Street Map");

        var gphy = new OpenLayers.Layer.Google(
            "Google Physical",
            {type: google.maps.MapTypeId.TERRAIN}
            // used to be {type: G_PHYSICAL_MAP}
        );
        var gmap = new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
            // default type, no change needed here
        );
        var ghyb = new OpenLayers.Layer.Google(
            "Google Hybrid",
            {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
            // used to be {type: G_HYBRID_MAP, numZoomLevels: 20}
        );
        var gsat = new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
            // used to be {type: G_SATELLITE_MAP, numZoomLevels: 22}
        );

        //TheMap.data.map.addLayer(osm);
        TheMap.data.map.addLayers([osm, gphy, gmap, ghyb, gsat]);

        TheMap.data.bounds = new OpenLayers.Bounds();


        center = TheMap.getLonLat(35.320333, -1.392895);

        zoom = 12;

        TheMap.data.map.setCenter(center, zoom);

        //position color-ramp
        var colors = ['#00FF00', '#0000FF', '#FF0000', '#01FFFE', '#FFA6FE', '#FFDB66', '#006401', '#010067', '#95003A', '#007DB5', '#FF00F6', '#FFEEE8', '#774D00', '#90FB92', '#0076FF', '#D5FF00', '#FF937E', '#6A826C', '#FF029D', '#FE8900', '#7A4782', '#7E2DD2', '#85A900', '#FF0056', '#A42400', '#00AE7E', '#683D3B', '#BDC6FF', '#263400', '#BDD393', '#00B917', '#9E008E', '#001544', '#C28C9F', '#FF74A3', '#01D0FF', '#004754', '#E56FFE', '#788231', '#0E4CA1', '#91D0CB', '#BE9970', '#968AE8', '#BB8800', '#43002C', '#DEFF74', '#00FFC6', '#FFE502', '#620E00', '#008F9C', '#98FF52', '#7544B1', '#B500FF', '#00FF78', '#FF6E41', '#005F39', '#6B6882', '#5FAD4E', '#A75740', '#A5FFD2', '#FFB167', '#009BFF', '#E85EBE'];

        var i = null;
        var getNextId = function() {
            if (i === null) {
                i = 0;
            } else {
                i++;
            }
            return i
        }

        var stylemap = new OpenLayers.StyleMap(
            {
                "default": new OpenLayers.Style(
                {
                    pointRadius: "${radius}",
                    fillColor: colors[getNextId()],
                    fillOpacity: 0.8,
                    strokeColor: colors[getNextId()],
                    strokeWidth: 2,
                    strokeOpacity: 0.8
                },
                {
                    context: {
                        radius: 2
                    }
                })
            }
        );

        var lionLayer = new OpenLayers.Layer.Vector(
                'Lions',
                {
                    strategies: [new OpenLayers.Strategy.Fixed()],
                    projection: TheMap.data.map.displayProjection,
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: "/kml/last/",
                        format: new OpenLayers.Format.KML({
                            extractStyles: true,
                            extractAttributes: true
                        })
                    }),
                    styleMap: stylemap
                }
            );

        var selectControl = new OpenLayers.Control.SelectFeature(lionLayer, {
                hover: true,
                clickout: true,
                highlightOnly: true,
                renderIntent: "temporary",
                eventListeners: {
                    //beforefeaturehighlighted: report,
                    featureunhighlighted: TheMap.onFeatureUnHighlighted,
                    featurehighlighted: TheMap.onFeatureHighlighted
                }
            });
        //selectControl.events.register('featurehighlighted', null, TheMap.onFeatureHighlighted);

        TheMap.data.lionLayers.push(lionLayer);
        TheMap.data.selectControl = selectControl ;

        TheMap.data.map.addLayers(TheMap.data.lionLayers);
        TheMap.data.map.addControl(TheMap.data.selectControl);

        TheMap.data.selectControl.activate();

    },

    heatmap : function() {
        TheMap.data.map = new OpenLayers.Map('map_canvas2', {
            controls: [
                new OpenLayers.Control.Navigation(),
                new OpenLayers.Control.PanZoomBar(),
                new OpenLayers.Control.LayerSwitcher({'ascending':false}),
                new OpenLayers.Control.ScaleLine(),
                new OpenLayers.Control.KeyboardDefaults()
            ]
        });
        var osm = new OpenLayers.Layer.OSM("Open Street Map");

        var gphy = new OpenLayers.Layer.Google(
            "Google Physical",
            {type: google.maps.MapTypeId.TERRAIN}
            // used to be {type: G_PHYSICAL_MAP}
        );
        var gmap = new OpenLayers.Layer.Google(
            "Google Streets", // the default
            {numZoomLevels: 20}
            // default type, no change needed here
        );
        var ghyb = new OpenLayers.Layer.Google(
            "Google Hybrid",
            {type: google.maps.MapTypeId.HYBRID, numZoomLevels: 20}
            // used to be {type: G_HYBRID_MAP, numZoomLevels: 20}
        );
        var gsat = new OpenLayers.Layer.Google(
            "Google Satellite",
            {type: google.maps.MapTypeId.SATELLITE, numZoomLevels: 22}
            // used to be {type: G_SATELLITE_MAP, numZoomLevels: 22}
        );

        //TheMap.data.map.addLayer(osm);
        TheMap.data.map.addLayers([osm, gphy, gmap, ghyb, gsat]);

        TheMap.data.bounds = new OpenLayers.Bounds();


        center = TheMap.getLonLat(35.320333, -1.392895);

        zoom = 12;

        TheMap.data.map.setCenter(center, zoom);

        //position color-ramp
        var colors = ['#00FF00', '#0000FF', '#FF0000', '#01FFFE', '#FFA6FE', '#FFDB66', '#006401', '#010067', '#95003A', '#007DB5', '#FF00F6', '#FFEEE8', '#774D00', '#90FB92', '#0076FF', '#D5FF00', '#FF937E', '#6A826C', '#FF029D', '#FE8900', '#7A4782', '#7E2DD2', '#85A900', '#FF0056', '#A42400', '#00AE7E', '#683D3B', '#BDC6FF', '#263400', '#BDD393', '#00B917', '#9E008E', '#001544', '#C28C9F', '#FF74A3', '#01D0FF', '#004754', '#E56FFE', '#788231', '#0E4CA1', '#91D0CB', '#BE9970', '#968AE8', '#BB8800', '#43002C', '#DEFF74', '#00FFC6', '#FFE502', '#620E00', '#008F9C', '#98FF52', '#7544B1', '#B500FF', '#00FF78', '#FF6E41', '#005F39', '#6B6882', '#5FAD4E', '#A75740', '#A5FFD2', '#FFB167', '#009BFF', '#E85EBE'];

        var i = null;
        var getNextId = function() {
            if (i === null) {
                i = 0;
            } else {
                i++;
            }
            return i
        }

        var stylemap = new OpenLayers.StyleMap(
            {
                "default": new OpenLayers.Style(
                {
                    pointRadius: "${radius}",
                    fillColor: colors[getNextId()],
                    fillOpacity: 0.8,
                    strokeColor: colors[getNextId()],
                    strokeWidth: 2,
                    strokeOpacity: 0.8
                },
                {
                    context: {
                        radius: 2
                    }
                })
            }
        );

        var lionLayer = new OpenLayers.Layer.Vector(
                'Lions',
                {
                    strategies: [new OpenLayers.Strategy.Fixed()],
                    projection: TheMap.data.map.displayProjection,
                    protocol: new OpenLayers.Protocol.HTTP({
                        url: "/kml/last/",
                        format: new OpenLayers.Format.KML({
                            extractStyles: true,
                            extractAttributes: true
                        })
                    }),
                    styleMap: stylemap
                }
            );

        var selectControl = new OpenLayers.Control.SelectFeature(lionLayer, {
                hover: true,
                clickout: true,
                highlightOnly: true,
                renderIntent: "temporary",
                eventListeners: {
                    //beforefeaturehighlighted: report,
                    featureunhighlighted: TheMap.onFeatureUnHighlighted,
                    featurehighlighted: TheMap.onFeatureHighlighted
                }
            });
        //selectControl.events.register('featurehighlighted', null, TheMap.onFeatureHighlighted);

        TheMap.data.lionLayers.push(lionLayer);
        TheMap.data.selectControl = selectControl ;

        TheMap.data.map.addLayers(TheMap.data.lionLayers);
        TheMap.data.map.addControl(TheMap.data.selectControl);

        TheMap.data.selectControl.activate();

    },

    getLonLat : function(lon, lat) {
        return new OpenLayers.LonLat( lon, lat )
            .transform(
                new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
                TheMap.data.map.getProjectionObject() // to Spherical Mercator Projection
            );
    }
};