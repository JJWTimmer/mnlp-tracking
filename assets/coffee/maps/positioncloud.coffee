#<< app/maps/basemap

class app.maps.PositionCloud extends app.maps.BaseMap
    constructor: (tag) ->
        super(tag)
        defs = @defaults
        map = @map
        $.getJSON "/lions", (data) ->
            lionLayers = []
            
            for lion, i in data['lions']
                style = new OpenLayers.Style(
                    {
                        pointRadius: "${radius}"
                        fillColor: defs.colors[i]
                        fillOpacity: 0.8
                        strokeColor: defs.colors[i]
                        strokeWidth: 2
                        strokeOpacity: 0.8
                    },
                    {
                        context:
                            radius: 2
                    }
                )
                stylemap = new OpenLayers.StyleMap(
                    'default': style
                    select:
                        fillColor: "#8aeeef"
                        strokeColor: "#32a8a9"
                )
                lionLayers.push new OpenLayers.Layer.Vector(
                    data["lions"][i]["name"],
                    strategies: [new OpenLayers.Strategy.Fixed()]
                    projection: map.displayProjection
                    protocol: new OpenLayers.Protocol.HTTP(
                        url: "/kml/lion/" + data["lions"][i]["id"] + "/"
                        format: new OpenLayers.Format.KML(
                            extractStyles: true
                            extractAttributes: true
                        )
                    )
                    styleMap: stylemap
                )

            map.addLayers lionLayers