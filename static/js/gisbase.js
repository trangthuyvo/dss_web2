$(document).ready(function () {
    // using jQuery
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



    // stations
    var stations_source = new ol.source.GeoJSON({
        projection: 'EPSG:4326',
        url: '/media/geojson/stations.js',
    });


    var stations_style = function () {
        var img = new ol.style.Circle({
            fill: new ol.style.Fill({
                color: 'rgba(250,5,5,1)'
            }),
            radius: 5,
            stroke: new ol.style.Stroke({
                color: 'rgba(250,5,5,1)',
                width: 1,
            })
        });
        var textStroke = new ol.style.Stroke({
            color: '#fff',
            width: 3
        });
        var textFill = new ol.style.Fill({
            color: '#000',
            visible: false,
        });


        //        var text_value = if(($("#Province-label")).is(':checked')){}
        return function (feature, resolution) {
            return [new ol.style.Style({
                image: img,
                text: new ol.style.Text({
                    font: '12px Calibri,sans-serif',
                    text: (function () {
                        if (($("#Station-label")).is(':checked')) {
                            return feature.get('name')
                        } else {
                            return ''
                        }
                    })(),
                    fill: textFill,
                    stroke: textStroke,
                    labelXOffset: '-10px',
                    labelYOffset: '-10px',
                }),
            })];
        };
    };


    var stations_layer = new ol.layer.Vector({
        source: stations_source,
        style: stations_style(),
    });

    // provinces
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
            visible: false,
        });
        var fill = new ol.style.Fill({
            color: 'rgba(250,5,5,0)'
        });

        //        var text_value = if(($("#Province-label")).is(':checked')){}
        return function (feature, resolution) {
            return [new ol.style.Style({
                stroke: stroke,
                fill: fill,
                text: new ol.style.Text({
                    font:  parseInt(5000/resolution)+'px Calibri,sans-serif',
                    text: (function () {
                        if (($("#Province-label")).is(':checked')) {
                            return feature.get('province')
                        } else {
                            return ''
                        }
                    })(),
                    fill: textFill,
                    stroke: textStroke,
                }),
            })];
        };
    };

    var provinces_source = new ol.source.GeoJSON({
        projection: 'EPSG:4326',
        url: '/media/geojson/provinces.js',
    });

    var provinces_layer = new ol.layer.Vector({
        source: provinces_source,
        style: provinces_style(),
        visible: false,
    });

    // landuse 
    landuse_color_code = {'TSN': 'rgba(170,255,255,1)', 'TSL': 'rgba(170,255,255,1)', 'NCS': 'rgba(230,230,200,1)', 'TSK': 'rgba(250,170,160,1)', 'SKS': 'rgba(205,170,205,1)', 'CTS': 'rgba(255,160,170,1)', 'LNQ': 'rgba(255,215,170,1)', 'HNK': 'rgba(255,240,180,1)', 'MVR': 'rgba(180,255,255,1)', 'TSC': 'rgba(255,170,160,1)', 'CCC': 'rgba(255,170,160,1)', 'LUA': 'rgba(255,252,130,1)', 'COC': 'rgba(230,230,130,1)', 'LUC': 'rgba(255,252,140,1)', 'TON': 'rgba(255,170,160,1)', 'SXN': 'rgba(255,252,110,1)', 'SKC': 'rgba(250,170,160,1)', 'DRA': 'rgba(205,170,205,1)', 'DKH': 'rgba(255,170,160,1)', 'LUK': 'rgba(255,252,150,1)', 'LUN': 'rgba(255,252,180,1)', 'DVH': 'rgba(255,170,160,1)', 'DBV': 'rgba(255,170,160,1)', 'CQP': 'rgba(255,100,80,1)', 'RPT': 'rgba(190,255,30,1)', 'DGD': 'rgba(255,170,160,1)', 'DYT': 'rgba(255,170,160,1)', 'DTL': 'rgba(170,255,255,1)', 'ODT': 'rgba(255,160,255,1)', 'LNP': 'rgba(170,255,50,1)', 'NHK': 'rgba(255,240,180,1)', 'SON': 'rgba(160,255,255,1)', 'SKK': 'rgba(250,170,160,1)', 'LNK': 'rgba(255,215,170,1)', 'CSD': 'rgba(255,255,254,1)', 'RPH': 'rgba(190,255,30,1)', 'RPK': 'rgba(190,255,30,1)', 'DTT': 'rgba(255,170,160,1)', 'RPM': 'rgba(190,255,30,1)', 'DCS': 'rgba(255,255,254,1)', 'ONT': 'rgba(255,208,255,1)', 'RPN': 'rgba(190,255,30,1)', 'RDT': 'rgba(110,255,100,1)', 'CLN': 'rgba(255,210,160,1)', 'MVT': 'rgba(180,255,255,1)', 'DGT': 'rgba(255,170,50,1)', 'CSK': 'rgba(255,160,170,1)', 'DNL': 'rgba(255,170,160,1)', 'DXH': 'rgba(255,170,160,1)', 'SMN': 'rgba(180,255,255,1)', 'BHK': 'rgba(255,240,180,1)', 'CHN': 'rgba(255,252,120,1)', 'SKX': 'rgba(205,170,205,1)', 'BCS': 'rgba(255,255,254,1)', 'RDD': 'rgba(110,255,100,1)', 'TTN': 'rgba(255,170,160,1)', 'MVK': 'rgba(180,255,255,1)', 'RDM': 'rgba(110,255,100,1)', 'RDN': 'rgba(110,255,100,1)', 'RDK': 'rgba(110,255,100,1)', 'TIN': 'rgba(255,170,160,1)', 'RSM': 'rgba(180,255,180,1)', 'RSN': 'rgba(180,255,180,1)', 'CDG': 'rgba(255,160,170,1)', 'DCH': 'rgba(255,170,160,1)', 'RSK': 'rgba(180,255,180,1)', 'NKH': 'rgba(245,255,180,1)', 'NTS': 'rgba(170,255,255,1)', 'OTC': 'rgba(255,180,255,1)', 'MVB': 'rgba(180,255,255,1)', 'LMU': 'rgba(255,255,254,1)', 'DDT': 'rgba(255,170,160,1)', 'PNK': 'rgba(255,170,160,1)', 'RSX': 'rgba(180,255,180,1)', 'LNC': 'rgba(255,215,170,1)', 'PNN': 'rgba(255,255,100,1)', 'RST': 'rgba(180,255,180,1)', 'MNC': 'rgba(180,255,255,1)', 'NNP': 'rgba(255,255,100,1)', 'NTD': 'rgba(210,210,210,1)', 'CAN': 'rgba(255,80,70,1)'}

    var landuse_style = function () {
        var stroke = new ol.style.Stroke({
            color: 'rgba(0,0,0,1)',
            width: 0.1,
        });
        var textStroke = new ol.style.Stroke({
            color: '#fff',
            width: 3
        });
        var textFill = new ol.style.Fill({
            color: '#000',
            visible: false,
        });


        return function (feature, resolution) {
            return [new ol.style.Style({
                stroke: stroke,
                fill: new ol.style.Fill({
                    color: (function () {
                        if (landuse_color_code[feature.get('code')]) {
                            return landuse_color_code[feature.get('code')]
                        } else {
                            return 'rgba(1,1,1,1)'
                        }
                    })()
                }),
                text: new ol.style.Text({
                    font:  parseInt(30/resolution) +'px Calibri,sans-serif',
                    text: (function () {
                        if (($("#Landuse-label")).is(':checked')) {
                            return feature.get('code')
                        } else {
                            return ''
                        }
                    })(),
                    fill: textFill,
//                    stroke: textStroke,
                }),
            })];
        };
    };

    var landuse_source = new ol.source.GeoJSON({
        projection: 'EPSG:4326',
        url: '/media/geojson/landuse.js',
    });

    var landuse_layer = new ol.layer.Vector({
        source: landuse_source,
        style: landuse_style(),
        visible: false,
    });



    var map = new ol.Map({
        target: 'map',
        layers: [
                  new ol.layer.Tile({
                //source: new ol.source.MapQuest({layer: 'osm'})
                source: new ol.source.OSM()

            })
                ,
                landuse_layer,
                provinces_layer,
                stations_layer,
                ],

        view: new ol.View({
            center: ol.proj.transform([106.32363, 11.20656], 'EPSG:4326', 'EPSG:3857'),
            zoom: 4,
        })
    });

    var visible_provinces = new ol.dom.Input(document.getElementById('Province'));
    visible_provinces.bindTo('checked', provinces_layer, 'visible');

    var visible_stations = new ol.dom.Input(document.getElementById('Station'));
    visible_stations.bindTo('checked', stations_layer, 'visible');

    var visible_landuse = new ol.dom.Input(document.getElementById('Landuse'));
    visible_landuse.bindTo('checked', landuse_layer, 'visible');

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

    $("#getzoom").click(function(){
        
        alert(map.getView().getResolution());
        });



});