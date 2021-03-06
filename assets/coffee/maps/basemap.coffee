#<< app/defaults

class app.maps.BaseMap
  constructor: (tag) ->
    @defaults = new app.Defaults
    @map = new OpenLayers.Map(tag, {
      controls: [
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.PanZoomBar(),
        new OpenLayers.Control.LayerSwitcher(ascending: false),
        new OpenLayers.Control.ScaleLine(),
        new OpenLayers.Control.KeyboardDefaults()
      ]
    })

    @osm = new OpenLayers.Layer.OSM("Open Street Map")

    @gphy = new OpenLayers.Layer.Google("Google Physical",
      type: google.maps.MapTypeId.TERRAIN
    )

    # the default
    @gmap = new OpenLayers.Layer.Google("Google Streets",
      numZoomLevels: 20
    )

    @ghyb = new OpenLayers.Layer.Google("Google Hybrid",
      type: google.maps.MapTypeId.HYBRID
      numZoomLevels: 20
    )

    @gsat = new OpenLayers.Layer.Google("Google Satellite",
      type: google.maps.MapTypeId.SATELLITE
      numZoomLevels: 22
    )

    @conservancy = new OpenLayers.Layer.Vector("Ol Kinyei Conservancy", {
      projection: @map.projection,
      strategies: [new OpenLayers.Strategy.Fixed()],
      protocol: new OpenLayers.Protocol.HTTP({
        url: "static/kml/OlKinyeied.kml",
        format: new OpenLayers.Format.KML({
          extractStyles: true,
          extractAttributes: true
        })
      }),
      displayInLayerSwitcher: false
    })


    @map.addLayers [@gphy, @osm, @gmap, @ghyb, @gsat, @conservancy]

    center = @getLonLat(@defaults.centerLongitude, @defaults.centerLatitude)
    zoom = @defaults.zoom
    @map.setCenter center, zoom

  getLonLat: (lon, lat) ->
    # transform from WGS 1984 to Spherical Mercator Projection
    (new OpenLayers.LonLat(lon, lat)).transform new OpenLayers.Projection("EPSG:4326"), @map.getProjectionObject()

  refresh: ->
    @map.updateSize()
