#<< app/maps/basemap

class app.maps.HeatMap extends app.maps.BaseMap
    constructor: (tag) ->
        super(tag)
        
        projWGS84 = new OpenLayers.Projection("EPSG:4326")
        bounds = new OpenLayers.Bounds(
            @defaults.minLat,
            @defaults.minLon,
            @defaults.maxLat,
            @defaults.maxLon
        )
        extent = bounds.transform(
            projWGS84,
            @map.getProjectionObject()
        )
        options = {
            isBaseLayer: false
            maxResolution: "auto"
            resolutions: @map.layers[0].resolutions
            projection: @map.getProjectionObject()
            strategies: [new OpenLayers.Strategy.Fixed()]
            displayInLayerSwitcher: true
            opacity: 1.0
        }
        
        
        $.getJSON("/heatmaplions", (data) =>
            heatmapLayers = []
            for lion in data.lions
                heatmapLayers.push new OpenLayers.Layer.Image(
                    lion,
                    "/heatmaps/#{lion}.png",
                    extent,
                    new OpenLayers.Size(1, 1),
                    options)
            @map.addLayers heatmapLayers
        )
        