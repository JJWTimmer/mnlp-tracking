#<< app/maps/basemap

class app.maps.LastPosition extends app.maps.BaseMap
    constructor: (tag) ->
        super(tag)
        
        i = null
        getNextId = ->
          if i is null
            i = 0
          else
            i++
          i

        stylemap = new OpenLayers.StyleMap('default': new OpenLayers.Style(
            {
                pointRadius: "${radius}"
                fillColor: @defaults.colors[getNextId()]
                fillOpacity: 0.8
                strokeColor: @defaults.colors[getNextId()]
                strokeWidth: 2
                strokeOpacity: 0.8
            },
            {
                context:
                    radius: 2
            }
        ))
        lionLayer = new OpenLayers.Layer.Vector("Lions",
          strategies: [new OpenLayers.Strategy.Fixed()]
          projection: @map.displayProjection
          protocol: new OpenLayers.Protocol.HTTP(
            url: "/kml/last/"
            format: new OpenLayers.Format.KML(
              extractStyles: true
              extractAttributes: true
            )
          )
          styleMap: stylemap
        )
        selectControl = new OpenLayers.Control.SelectFeature(lionLayer,
          hover: true
          clickout: true
          highlightOnly: true
          renderIntent: "temporary"
          eventListeners:
            featureunhighlighted: @onFeatureUnHighlighted
            featurehighlighted: @onFeatureHighlighted
        )

        @map.addLayer lionLayer
        @map.addControl selectControl
        selectControl.activate()
        
    onFeatureHighlighted: (evt) ->
        # Needed only for interaction, not for the display.
        onPopupClose = (evt) ->
            # 'this' is the popup.
            feature = @feature
            TheMap.data.selectControl.unselect feature  if feature.layer
            @destroy()

        feature = evt.feature
        popup = new OpenLayers.Popup.FramedCloud("featurePopup", feature.geometry.getBounds().getCenterLonLat(), null, "<h2>" + feature.data.name + "</h2><p>" + feature.data.description + "</p>", null, true, onPopupClose)
        feature.popup = popup
        popup.feature = feature
        @map.addPopup popup, true

    onFeatureUnHighlighted: (evt) ->
        i = 0
        
        while i < @map.popups.length
            @map.popups[i].hide()
            @map.popups[i].destroy()
            i++