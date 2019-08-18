function init_map() {
    'use strict';

    var map = new google.maps.Map(document.getElementById('odoo-polygon-map'), {
        zoom: 100,
        center: {lat: 16.8661, lng: 96.1951},
        mapTypeId: google.maps.MapTypeId.ROADMAP
    });
    
    // Add Point and create Polygon on the map
    if (odoo_partner_data){ /* odoo_partner_data special variable should have been defined in google_map.xml */
        var triangleCoords = [];
        for (var i = 0; i < odoo_partner_data.counter; i++) {
            var addPoint = {
                lat: parseFloat(odoo_partner_data.partners[i].latitude), 
                lng: parseFloat(odoo_partner_data.partners[i].longitude)
            };
            triangleCoords.push(addPoint);
            console.log('triangleCoords');
            console.log(triangleCoords);            
        }
        var endPoint = {
            lat: parseFloat(odoo_partner_data.partners[0].latitude), 
            lng: parseFloat(odoo_partner_data.partners[0].longitude)
        };
        triangleCoords.push(endPoint);
        // Construct the polygon.
        var bermudaTriangle = new google.maps.Polygon({
            paths: triangleCoords,
            strokeColor: '#FF0000',
            strokeOpacity: 0.8,
            strokeWeight: 2,
            fillColor: '#FF0000',
            fillOpacity: 0.35
        });
        bermudaTriangle.setMap(map);
    }
}

// Initialize map once the DOM has been loaded
google.maps.event.addDomListener(window, 'load', init_map);
