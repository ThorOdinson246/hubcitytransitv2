
var show_bus_stops = false;
var show_green_bus_stops = false;
var busStopsLayer = L.layerGroup();
var buttonContainer = document.getElementById("button-container");
var update_eta_button = document.getElementById("eta-box");


var map = L.map("map").setView([31.3271, -89.2903], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
}).addTo(map);

function getIcon() {
  return L.icon({
    iconUrl:
      "https://freeiconshop.com/wp-content/uploads/edd/location-arrow-flat.png",
    iconSize: [25, 25],
    popupAnchor: [-3, -76],
  });
}

function getAwesomeMarker(color) {
  return L.AwesomeMarkers.icon({
    icon: "info-sign",
    markerColor: color,
    prefix: "glyphicon",
  });
}

var busMarker = L.marker([31.3271, -89.2903], { icon: getIcon() })
  .bindTooltip("Bus")
  .addTo(map);

navigator.geolocation.getCurrentPosition(
  function (position) {
    var userLat = position.coords.latitude;
    var userLng = position.coords.longitude;
    userLocationMarker = L.marker([userLat, userLng], { icon: getIcon() })
      .bindTooltip("Me")
      .addTo(map);
  },
  function (error) {
    console.error("Error getting user location: " + error.message);
  }
);

function updateBusLocation() {
  fetch("/bus_location")
    .then((response) => response.json())
    .then((data) => {
      var location = data.location;
      if (location[0] && location[1]) {
        busMarker.setLatLng([location[0], location[1]]);
        // also update the bus marker's tooltip
        busMarker.bindTooltip("Bus: " + data.bus_id);
      }
      // console.debug("updating bus location");
    });
}

function fetchBusStops() {
  fetch("/bus_stops")
    .then((response) => response.json())
    .then((data) => {
      var buttonContainer = document.getElementById("button-container");

      // Create layers for each bus stop
      var busStopLayers = {};

      // Function to create a button for each bus stop
      function createButton(stopName, stopData) {
        var button = document.createElement("button");
        button.textContent = `Toggle ${stopName}`;
        button.className = "route-button";
        button.onclick = function () {
          if (map.hasLayer(busStopLayers[stopName])) {
            map.removeLayer(busStopLayers[stopName]); // Hide bus stop
            button.textContent = `Show ${stopName}`;
          } else {
            map.addLayer(busStopLayers[stopName]); // Show bus stop
            button.textContent = `Hide ${stopName}`;
          }
        };
        buttonContainer.appendChild(button);
      }

      // Process blue route stops
      busStopLayers["Blue Route Stops"] = L.layerGroup();
      data.blue_stops.forEach((stop) => {
        L.marker([stop.x, stop.y])
          .addTo(busStopLayers["Blue Route Stops"])
          .bindPopup(`${stop.location}: ${stop.stop_id}`);
      });
      createButton("Blue Route Stops", data.blue_stops);

      busStopLayers["Gold Route Stops"] = L.layerGroup();
      data.gold_stops.forEach((stop) => {
        L.marker([stop.x, stop.y])
          .addTo(busStopLayers["Gold Route Stops"])
          .bindPopup(`${stop.location}: ${stop.stop_id}`);
      });
      createButton("Gold Route Stops", data.gold_stops);

      // Process green route stops
      busStopLayers["Green Route Stops"] = L.layerGroup();
      data.green_stops.forEach((stop) => {
        L.marker([stop.x, stop.y])
          .addTo(busStopLayers["Green Route Stops"])
          .bindPopup(`${stop.location}: ${stop.stop_id}`);
      });
      createButton("Green Route Stops", data.green_stops);
    })
    .catch((error) => console.error("Error fetching bus stops: ", error));
}
fetchBusStops();

setInterval(updateBusLocation, 5000);

// Fetch routes from the server
fetch("/routes")
  .then((response) => response.json())
  .then((data) => {
    console.log(data); // Debugging: Log the data to the console

    // Create polylines for each route
    var blueRoute = L.polyline(data.blue_route, {
      color: "#486dff",
      weight: 5.0,
    });
    var goldRoute = L.polyline(data.gold_route, {
      color: "#f8d700",
      weight: 5.0,
    });
    var greenRoute = L.polyline(data.green_route, {
      color: "#5fbf00",
      weight: 5.0,
    });
    var brownRoute = L.polyline(data.brown_route, {
      color: "#3b1e0a",
      weight: 5.0,
    });
    var orangeRoute = L.polyline(data.orange_route, {
      color: "#ff6f00",
      weight: 5.0,
    });
    var redRoute = L.polyline(data.red_route, {
      color: "#ff0000",
      weight: 5.0,
    });
    var purpleRoute = L.polyline(data.purple_route, {
      color: "#800080",
      weight: 5.0,
    });

    // Create and add buttons to toggle routes

    function createRouteButton(route, color, routeName) {
      var button = document.createElement("button");
      button.textContent = `Show ${routeName} Route`;
      button.className = "route-button";
      button.onclick = function () {
        if (map.hasLayer(route)) {
          map.removeLayer(route);
          button.textContent = `Show ${routeName} Route`;
        } else {
          map.addLayer(route);
          button.textContent = `Hide ${routeName} Route`;
        }
      };
      buttonContainer.appendChild(button);
    }

    createRouteButton(blueRoute, "#3a72ff", "Blue");
    createRouteButton(goldRoute, "#ffcc00", "Gold");
    createRouteButton(greenRoute, "#53a600", "Green");
  })
  .catch((error) => console.error("Error fetching routes:", error));

  function create_update_eta_button() {
    var button = document.createElement("button");
    button.textContent = "Update ETA";
    button.className = "route-button";
    button.onclick = function () {
      updateETA();
    };
    buttonContainer.appendChild(button);
  }

create_update_eta_button();

function updateETA() {
  // Simple fetch without content-type for GET request
  fetch("/get_eta")
    .then((response) => response.json())
    .then((data) => {
      var etaBox = document.getElementById("eta-box");
      etaBox.onclick = function () {
        updateETA();
      };
      if (data.eta) {
        etaBox.innerHTML = `ETA: ${data.eta} (Bus: ${data.bus_tracked})`;
      } else {
        etaBox.innerHTML = "ETA unavailable";
      }
    })
    .catch((error) => {
      console.error("Error fetching ETA:", error);
      var etaBox = document.getElementById("eta-box");
      etaBox.innerHTML = "Error fetching ETA";
    });
}

function getUserLocationAndSendToBackend() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      function (position) {
        var userLat = position.coords.latitude;
        var userLng = position.coords.longitude;
        console.log("User location:", userLat, userLng);

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
            // updateETA();
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

function changeBusTracking() {
  const selectedBus = document.getElementById("busSelect").value;

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

      
    })
    .catch((error) => {
      console.error("Error updating bus tracking:", error);
    });
}
getUserLocationAndSendToBackend();
// updateETA();
