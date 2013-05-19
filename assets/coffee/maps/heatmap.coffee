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


    $.getJSON("/lions", (liondata) =>
      heatmapLayers = []
      for lion in liondata.lions
        heatmapLayers.push new OpenLayers.Layer.Heatmap(
          lion.name,
          @map,
          @osm,
          {visible: true, radius: 10},
          {isBaseLayer: false, opacity: 0.3, projection: projWGS84}
        )
      @map.addLayers heatmapLayers

      $.each liondata.lions, (i, lion) =>
        $.getJSON("/json/lion/#{lion.id}", (positiondata) =>
          heatmapLayers[i].setDataSet(@transform(positiondata))
        )


    )

  transform: (positiondata) =>
    {
      max: positiondata.max,
      data: ({lonlat: new OpenLayers.LonLat(pos.lon, pos.lat), count: pos.count} for pos in positiondata.data)
    }