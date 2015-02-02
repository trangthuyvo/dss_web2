{% load static %} 
{% load return_item %}
$(document).ready(function () {
     using jQuery
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');


    ////
    $("#layer-manager").click(function () {
        $("#layers").toggle();
    });

    $(function () {
        $("#layers").draggable();
    });



    var longlat = [];




    var stations_source = new ol.source.GeoJSON({
        projection: 'EPSG:4326',
        url: '/media/geojson/stations.js',
    });
    
    var stations_style = {
        'Point': [new ol.style.Style({
                image: new ol.style.Circle({
                    fill: new ol.style.Fill({
                        color: 'rgba(250,5,5,1)'
                    }),
                    radius: 5,
                    stroke: new ol.style.Stroke({
                        color: 'rgba(250,5,5,1)',
                        width: 1,
                    })
                })
            })
                        ],
    };
    var stations_layer = new ol.layer.Vector({
        source: stations_source,
        style: stations_style['Point'],
    });


    var provinces_style = function () {
        var stroke = new ol.style.Stroke({
            color: 'rgba(80,238,247,1)',
            width: 2,
        });
        var textStroke = new ol.style.Stroke({
            color: '#fff',
            width: 3
        });
        var textFill = new ol.style.Fill({
            color: '#000',
        });
        var fill = new ol.style.Fill({
            color: 'rgba(250,5,5,0)'
        });
        return function (feature, resolution) {
            return [new ol.style.Style({
                stroke: stroke,
                fill: fill,
                text: new ol.style.Text({
                    font: '12px Calibri,sans-serif',
                    text: feature.get('province'),
                    fill: textFill,
                    stroke: textStroke,
                }),
            })];
        };
    };

    var provinces_source = new ol.source.GeoJSON({
        projection: 'EPSG:4326',
        url: '/media/geojson/provinces.js',,
    });

    var provinces_layer = new ol.layer.Vector({
        source: provinces_source,
        style: provinces_style(),
    });

    
    var map = new ol.Map({
        target: 'map',
        layers: [
                  new ol.layer.Tile({
                //source: new ol.source.MapQuest({layer: 'osm'})
                source: new ol.source.OSM()

            })
                ,
                stations_layer,
                provinces_layer
                ],

        view: new ol.View({
            center: ol.proj.transform([106.32363, 11.20656], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4
        })
    });

    var visible_provinces = new ol.dom.Input(document.getElementById('Province'));
    visible_provinces.bindTo('checked', provinces_layer, 'visible');

    var visible_stations = new ol.dom.Input(document.getElementById('Station'));
    visible_stations.bindTo('checked', stations_layer, 'visible');

    // add drag box


    var select = new ol.interaction.Select();
    map.addInteraction(select);

    var selectedFeatures = select.getFeatures();


    // a DragBox interaction used to select features by drawing boxes
    var dragBox = new ol.interaction.DragBox({
        condition: ol.events.condition.shiftKeyOnly,
        style: new ol.style.Style({
            stroke: new ol.style.Stroke({
                color: [0, 0, 255, 1]
            })
        })
    });
    map.addInteraction(dragBox);


    var infoBox = document.getElementById('info');
    var id = [];
    var name = [];
    dragBox.on('boxend', function (evt) {
        // features that intersect the box are added to the collection of
        // selected features, and their names are displayed in the "info"
        // div

        var info = [];
        var extent = dragBox.getGeometry().extent;

        stations_source.forEachFeatureInExtent(extent, function (feature) {
            selectedFeatures.push(feature);
            info.push(feature.get('name'));
            id.push(feature.get('id'));
            name.push(feature.get('name'));
        });
        if (info.length > 0) {
            infoBox.innerHTML = info.join(', ');
        }
    });


    // clear selection when drawing a new box and when clicking on the map
    dragBox.on('boxstart', function (e) {
        var id = [];
        var name = [];
        selectedFeatures.clear();
        infoBox.innerHTML = '&nbsp;';
    });
    map.on('click', function () {
        var id = [];
        var name = [];
        selectedFeatures.clear();
        infoBox.innerHTML = '&nbsp;';
    });

    // send id request to backend

    $("#data-review").click(function () {
        console.log(id);

        $.ajax({
            type: 'POST',
            url: 'data_review',
            data: {
                'id[]': id,
//                'name[]': name,
//                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            success: function (newdata) {
                $('body').html(newdata);
                
            },
            error: function () {
                alert("Failed in sending ajax request")
            },
            dataType: 'html',
            headers: {
                'X-CSRFToken': csrftoken
            }

        });

    });


});