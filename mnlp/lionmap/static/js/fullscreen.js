// color ramp with distinct colors
var colors = ["#00FF00", "#0000FF", "#FF0000", "#01FFFE", "#FFA6FE", "#FFDB66", "#006401", "#010067", "#95003A", "#007DB5", "#FF00F6", "#FFEEE8", "#774D00", "#90FB92", "#0076FF", "#D5FF00", "#FF937E", "#6A826C", "#FF029D", "#FE8900", "#7A4782", "#7E2DD2", "#85A900", "#FF0056", "#A42400", "#00AE7E", "#683D3B", "#BDC6FF", "#263400", "#BDD393", "#00B917", "#9E008E", "#001544", "#C28C9F", "#FF74A3", "#01D0FF", "#004754", "#E56FFE", "#788231", "#0E4CA1", "#91D0CB", "#BE9970", "#968AE8", "#BB8800", "#43002C", "#DEFF74", "#00FFC6", "#FFE502", "#620E00", "#008F9C", "#98FF52", "#7544B1", "#B500FF", "#00FF78", "#FF6E41", "#005F39", "#6B6882", "#5FAD4E", "#A75740", "#A5FFD2", "#FFB167", "#009BFF", "#E85EBE"];

// POSITION MAP

var lionmap = L.map('map_canvas', {
    center: [-1.392895, 35.320333],
    zoom: 12
});

var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
var osmAttrib = 'Map data © OpenStreetMap contributors';
var osm = new L.TileLayer(osmUrl, {minZoom: 1, maxZoom: 20, attribution: osmAttrib});

lionmap.addLayer(osm);

$.getJSON("/liondata").success(function (data) {

    var featureIndex = 0;

    var geojsonMarkerOptions = {
        radius: 4,
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    };

    L.geoJson(data, {
        style: function (feature) {
            return {color: colors[featureIndex++]};
        },
        pointToLayer: function (feature, latlng) {
            return L.circleMarker(latlng, geojsonMarkerOptions);
        },
        onEachFeature: function (feature, layer) {
            if (feature.properties && feature.properties.lion) {
                layer.bindPopup(feature.properties.lion);
            } else if (feature.properties && feature.properties.timestamp) {
                layer.bindPopup(feature.properties.timestamp);
            }
        }
    }).addTo(lionmap);
});

$.getJSON("/static/kml/OlKinyeied.json").success(function (data) {
    var onFeature = function (feature, layer) {
        if ('properties' in feature && 'Name' in feature.properties) {
            layer.bindPopup(feature.properties.Name);
        }
    };

    L.geoJson(data, {onEachFeature: onFeature}).addTo(lionmap);
});
