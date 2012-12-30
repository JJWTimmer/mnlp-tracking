
var transform = function(lon, lat, map) {
        return new OpenLayers.LonLat( lon, lat )
            .transform(
                new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
                map.getProjectionObject() // to Spherical Mercator Projection
            );
    };

var map = new OpenLayers.Map('map', {
    controls: [
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.PanZoomBar(),
        new OpenLayers.Control.LayerSwitcher({'ascending':false}),
        new OpenLayers.Control.ScaleLine(),
        new OpenLayers.Control.KeyboardDefaults()
    ]
});

    
var osm = new OpenLayers.Layer.OSM("Open Street Map");
map.addLayer(osm);

var options = {
    //numZoomLevels: 15,
    isBaseLayer: false,
    maxResolution: "auto",
    resolutions: map.layers[0].resolutions,
    projection: map.getProjectionObject(),
    strategies: [new OpenLayers.Strategy.Fixed()],
    displayInLayerSwitcher: true,
    opacity: 1.0
};

var projWGS84 = new OpenLayers.Projection("EPSG:4326");

var extent = new OpenLayers.Bounds(4.874668, 52.353377, 4.926167, 52.384820)
        .transform(projWGS84, map.getProjectionObject());
        
var ovl = new OpenLayers.Layer.Image(
    "Overlay",
    "http://localhost:8000/static/foo.png",
    extent,
    new OpenLayers.Size(1, 1),
    options
);
        
map.addLayer(ovl);
var center = new OpenLayers.LonLat( 4.900, 52.371 )
            .transform(
                new OpenLayers.Projection("EPSG:4326"), // transform from WGS 1984
                map.getProjectionObject() // to Spherical Mercator Projection
            );
var zoom = 13;
map.setCenter(center, zoom);