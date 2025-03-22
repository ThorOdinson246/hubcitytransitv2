// Global variables
var map = L.map("map").setView([31.3271, -89.2903], 13);
var busMarker;
var userLocationMarker;
var routeLayers = {};
var busStopLayers = {};

// Initialize map

// My JawgStreet Tile 
// L.tileLayer("https://tile.jawg.io/97b19866-a190-42fe-ac4c-ba4304040d6c/{z}/{x}/{y}{r}.png?access-token=1CwmLkVr2ikIlXq08byS0C1kXLOVadzTlkvX6OcZonoj1CLP7f75ZmiKRhzj8GUI", {
//     maxZoom: 19,
//     attribution:'<a href="https://jawg.io?utm_medium=map&utm_source=attribution" title="Tiles Courtesy of Jawg Maps" target="_blank" class="jawg-attrib" >&copy; <b>Jawg</b>Maps</a> | <a href="https://www.openstreetmap.org/copyright" title="OpenStreetMap is open data licensed under ODbL" target="_blank" class="osm-attrib">&copy; OSM contributors</a>'
// }).addTo(map);

// Default Leaflet
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

function getBusIcon() {
    return L.icon({
        iconUrl: '/bus_icon',
        iconSize: [25, 25],
        popupAnchor: [-3, -76],
    });
}

function getMeIcon() {
  return L.icon({
      iconUrl: '/me_icon',
      iconSize: [25, 25],
      popupAnchor: [-3, -76],
  });
}

// Initialize bus marker
busMarker = L.marker([31.3271, -89.2903], { icon: getBusIcon() })
    .bindTooltip("Bus")
    .addTo(map);

// Get user location
function getUserLocationAndSendToBackend() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            function (position) {
                var userLat = position.coords.latitude;
                var userLng = position.coords.longitude;
                
                if (userLocationMarker) {
                    userLocationMarker.setLatLng([userLat, userLng]);
                } else {
                    userLocationMarker = L.marker([userLat, userLng], { icon: getMeIcon() })
                        .bindTooltip("Me")
                        .addTo(map);
                }
                
                // Send location to backend
                fetch("/user_location", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        user_lat: userLat,
                        user_lng: userLng,
                    }),
                })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Location sent successfully to backend:", data);
                })
                .catch((error) => {
                    console.error("Error sending location:", error);
                });
            },
            function (error) {
                console.error("Error getting user location: " + error.message);
            }
        );
    } else {
        console.error("Geolocation is not supported by this browser.");
    }
}

// Update bus location
function updateBusLocation() {
    fetch("/bus_location")
        .then((response) => response.json())
        .then((data) => {
            var location = data.location;
            if (location && location.length === 2) {
                busMarker.setLatLng([location[0], location[1]]);
                busMarker.setTooltipContent("Bus: " + data.bus_id);
            }
        })
        .catch((error) => {
            console.error("Error updating bus location:", error);
        });
}

// Initialize bus stops
function fetchBusStops() {
    fetch("/bus_stops")
        .then((response) => response.json())
        .then((data) => {
            var buttonContainer = document.getElementById("route-buttons");
            if (!buttonContainer) {
                console.error("Could not find route-buttons container");
                return;
            }
            
            // Clear existing buttons
            buttonContainer.innerHTML = '';
            
            // Process blue route stops
            busStopLayers["blue_stops"] = L.layerGroup();
            data.blue_stops.forEach((stop) => {
                L.marker([stop.x, stop.y])
                    .bindPopup(`${stop.location}: ${stop.stop_id}`)
                    .addTo(busStopLayers["blue_stops"]);
            });
            createStopButton("blue_stops", "Blue Stops", buttonContainer);
            
            // Process gold route stops
            busStopLayers["gold_stops"] = L.layerGroup();
            data.gold_stops.forEach((stop) => {
                L.marker([stop.x, stop.y])
                    .bindPopup(`${stop.location}: ${stop.stop_id}`)
                    .addTo(busStopLayers["gold_stops"]);
            });
            createStopButton("gold_stops", "Gold Stops", buttonContainer);
            
            // Process green route stops
            busStopLayers["green_stops"] = L.layerGroup();
            data.green_stops.forEach((stop) => {
                L.marker([stop.x, stop.y])
                    .bindPopup(`${stop.location}: ${stop.stop_id}`)
                    .addTo(busStopLayers["green_stops"]);
            });
            createStopButton("green_stops", "Green Stops", buttonContainer);
        })
        .catch((error) => {
            console.error("Error fetching bus stops:", error);
        });
}

// Create button for stops
function createStopButton(stopId, displayName, container) {
    var button = document.createElement("button");
    button.textContent = `Show ${displayName}`;
    button.className = "stop-button";
    button.setAttribute('data-stops', stopId);
    
    button.addEventListener('click', function() {
        toggleStops(stopId);
    });
    
    container.appendChild(button);
}

// Toggle stops visibility
function toggleStops(stopId) {
    var button = document.querySelector(`[data-stops="${stopId}"]`);
    if (!button) {
        console.error(`Button for ${stopId} not found`);
        return;
    }
    
    if (map.hasLayer(busStopLayers[stopId])) {
        map.removeLayer(busStopLayers[stopId]);
        button.textContent = `Show ${stopId.split('_')[0].charAt(0).toUpperCase() + stopId.split('_')[0].slice(1)} Stops`;
        button.classList.remove("active");
    } else {
        map.addLayer(busStopLayers[stopId]);
        button.textContent = `Hide ${stopId.split('_')[0].charAt(0).toUpperCase() + stopId.split('_')[0].slice(1)} Stops`;
        button.classList.add("active");
    }
}

// Fetch and initialize routes
function fetchRoutes() {
    fetch("/routes")
        .then((response) => response.json())
        .then((data) => {
            var buttonContainer = document.getElementById("stop-buttons");
            if (!buttonContainer) {
                console.error("Could not find stop-buttons container");
                return;
            }
            
            // Clear existing buttons
            buttonContainer.innerHTML = '';
            
            // Create blue route
            routeLayers["blue"] = L.polyline(data.blue_route, {
                color: "#486dff",
                weight: 5.0,
            });
            createRouteButton("blue", "#486dff", "Blue", buttonContainer);
            
            // Create gold route
            routeLayers["gold"] = L.polyline(data.gold_route, {
                color: "#f8d700",
                weight: 5.0,
            });
            createRouteButton("gold", "#f8d700", "Gold", buttonContainer);
            
            // Create green route
            routeLayers["green"] = L.polyline(data.green_route, {
                color: "#5fbf00",
                weight: 5.0,
            });
            createRouteButton("green", "#5fbf00", "Green", buttonContainer);
        })
        .catch((error) => {
            console.error("Error fetching routes:", error);
        });
}

// Create button for routes
function createRouteButton(routeId, color, displayName, container) {
    var button = document.createElement("button");
    button.textContent = `Show ${displayName} Route`;
    button.className = "route-button";
    button.setAttribute('data-route', routeId);
    
    button.addEventListener('click', function() {
        toggleRoute(routeId);
    });
    
    container.appendChild(button);
}

// Toggle route visibility
function toggleRoute(routeId) {
    var button = document.querySelector(`[data-route="${routeId}"]`);
    if (!button) {
        console.error(`Button for ${routeId} not found`);
        return;
    }
    
    if (map.hasLayer(routeLayers[routeId])) {
        map.removeLayer(routeLayers[routeId]);
        button.textContent = `Show ${routeId.charAt(0).toUpperCase() + routeId.slice(1)} Route`;
        button.classList.remove("active");
    } else {
        map.addLayer(routeLayers[routeId]);
        button.textContent = `Hide ${routeId.charAt(0).toUpperCase() + routeId.slice(1)} Route`;
        button.classList.add("active");
    }
}

// Update ETA information
function updateETA() {
    var etaDisplay = document.getElementById("eta-display");
    if (!etaDisplay) {
        console.error("ETA display element not found");
        return;
    }
    
    etaDisplay.innerHTML = '<span class="eta-value">Loading...</span>';
    
    fetch("/get_eta")
        .then((response) => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then((data) => {
            if (data && data.eta) {
                etaDisplay.innerHTML = `<span class="eta-value">${data.eta} (${data.bus_tracked})</span>`;
            } else {
                etaDisplay.innerHTML = '<span class="eta-value">No ETA available</span>';
            }
        })
        .catch((error) => {
            console.error("Error fetching ETA:", error);
            etaDisplay.innerHTML = '<span class="eta-value">Error updating ETA</span>';
        });
}

// Change which bus to track
function changeBusTracking() {
    const selectedBus = document.getElementById("busSelect").value;
    
    if (!selectedBus) {
        console.warn("No bus selected for tracking");
        return;
    }
    
    fetch("/track_bus", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            bus_to_track: selectedBus,
        }),
    })
    .then((response) => response.json())
    .then((data) => {
        console.log("Bus tracking updated:", data);
        updateBusLocation();
        
        // Show route for selected bus
        var routeType = selectedBus.includes("blue") ? "blue" : 
                       (selectedBus.includes("gold") ? "gold" : 
                       (selectedBus === "green" ? "green" : ""));
        
        if (routeType && !map.hasLayer(routeLayers[routeType])) {
            toggleRoute(routeType);
        }
        
        // Update ETA after changing bus
        // updateETA();//Costs money yaar, not this. 
    })
    .catch((error) => {
        console.error("Error updating bus tracking:", error);
    });
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile panel toggle functionality for routes
        // Mobile panel toggle functionality for routes
    const routesPanel = document.getElementById('routesPanel');
    const routesPanelToggle = document.getElementById('routesPanelToggle');
    
    if (routesPanelToggle && routesPanel) {
        routesPanelToggle.addEventListener('click', function() {
            // Close stops panel if open
            if (stopsPanel && stopsPanel.classList.contains('active')) {
                stopsPanel.classList.remove('active');
            }
            routesPanel.classList.toggle('active');
        });
    }
    
    // Mobile panel toggle functionality for stops
    const stopsPanel = document.getElementById('stopsPanel');
    const stopsPanelToggle = document.getElementById('stopsPanelToggle');
    
    if (stopsPanelToggle && stopsPanel) {
        stopsPanelToggle.addEventListener('click', function() {
            // Close routes panel if open
            if (routesPanel && routesPanel.classList.contains('active')) {
                routesPanel.classList.remove('active');
            }
            stopsPanel.classList.toggle('active');
        });
    }

    map.on('click', function() {
      if (routesPanel && routesPanel.classList.contains('active')) {
          routesPanel.classList.remove('active');
      }
      if (stopsPanel && stopsPanel.classList.contains('active')) {
          stopsPanel.classList.remove('active');
      }
  });

  
    // Update ETA button
    const updateETABtn = document.getElementById('updateETABtn');
    if (updateETABtn) {
        updateETABtn.addEventListener('click', updateETA);
    }
    
    // Bus selector
    const busSelect = document.getElementById('busSelect');
    if (busSelect) {
        busSelect.addEventListener('change', changeBusTracking);
    }
    
    // Initialize app
    fetchBusStops();
    fetchRoutes();
    getUserLocationAndSendToBackend();
    updateBusLocation();
    
    // Set up interval for bus location updates
    setInterval(updateBusLocation, 5000);
});
