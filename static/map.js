    // Initialize the map

    var lati = document.getElementById('latitude').value
    var long = document.getElementById('longitude').value
    const map = L.map('map').setView([lati, long], 2); // Default to world view

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 20,
        minZoom: 1
    }).addTo(map);

    // Add a marker
    let marker = L.marker([lati, long], { draggable: true }).addTo(map);

    // Update latitude and longitude inputs when marker is dragged
    marker.on('dragend', function (e) {
        const { lat, lng } = e.target.getLatLng();
        document.getElementById('latitude').value = lat.toFixed(6);
        document.getElementById('longitude').value = lng.toFixed(6);
    });

    // Allow user to click on map to place the marker
    map.on('click', function (e) {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        document.getElementById('latitude').value = lat.toFixed(6);
        document.getElementById('longitude').value = lng.toFixed(6);
    });