# HubCityTransit Bus Tracker v2

>  **Note — Updated February 23, 2026**  
> The project has a new homepage and a new frontend techstack at [HubCityTransitV2](https://hubcityv2.mukeshpoudel.com.np). Please feel free to checkout the new updated look. 

>  **Note — Updated January 26, 2026**  
> It has come to my attention that the ArcGIS feature URL APIs previously used by this project are **no longer publicly accessible**.  
> As a result, some parts of the application may **not function as expected**, including map layers and live data retrieval. The project may require updated data sources or authenticated endpoints to restore full functionality.
>
> 

This project is a streamlined version of the existing [HubCityTransit map](https://hubcitytransit.com/map). The system uses the ArcGIS API to fetch bus locations and the Google Maps API to calculate ETAs. The frontend is built using Leaflet for map rendering and jQuery for AJAX requests while the backend is powered by Flask to handle API requests and data processing..

This project started as a fun experiment because the original map service was too cluttered with very little customizability on which bus to view and hiding specific layers and stops. Unlike the original map, my rendition focuses on just three essential routes for now: Blue, Green, and Gold. and implements a real-time ETA functionality using the Google Maps API and a user friendly interface.

I initially created and deployed this for my own use to navigate inside and around campus, but have decided to make it public to benefit others who might find it useful. I will continue to publish updates and improvemenets to this project over time. 

A deployed version of this repository can be accessed at  [HubCityV2](https://hubcityv2.mukeshpoudel.com.np)

## Features

- Real-time bus location tracking
- Interactive map with bus routes and stops
- ETA calculation for buses based on user location
- Toggle visibility of routes and bus stops
- User-friendly interface 

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ThorOdinson246/hubcitytransitv2.git
   cd hubcitytransitv2
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your own Google Maps API key.

## Usage

1. Start the Flask application:

   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000` to view the bus tracker.

## Key Components

### Data Extraction

#### `getDataFromArcGIS.py`

This file contains the `getDataFromArcGIS` class, which was purely created to fetch data from an ArcGIS feature layer and understand the structure of the returned data. The feature layer url used for this project is [FEATURE_LAYER](https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1
)

```python
class getDataFromArcGIS:
    def __init__(self, feature_layer_url):
        from arcgis.gis import GIS
        from arcgis.features import FeatureLayer

        self.gis = GIS()
        self.feature_layer = FeatureLayer(feature_layer_url)

    def fetch_data(self):
        self.features = self.feature_layer.query().features

    def print_data(self):
        for feature in self.features:
            print(feature.attributes)

    def save_data_to_json(self, file_path):
        import json
        with open(file_path, 'w') as json_file:
            json.dump(
                [feature.attributes for feature in self.features], json_file, indent=2)

```

#### `extract_bus_stops_from_mega_file.py`

To get the bus stops, I utilized the REST API endpoint provided by ArcGIS Online to access the web map's configuration. The JSON file was downloaded from the following URL: [ArcGIS JSON Data](https://www.arcgis.com/sharing/rest/content/items/512d08660aec4c61ab6796d098a03f3b/data?f=json). The web map can be viewed here: [ArcGIS Web Map](https://hattiesburgms.maps.arcgis.com/apps/mapviewer/index.html?webmap=512d08660aec4c61ab6796d098a03f3b)

```python
extract_bus_stops(input_file, output_file)`**:
.....
for operational_layer in data.get('operationalLayers', []):
            feature_collection = operational_layer.get('featureCollection', {})
            for layer in feature_collection.get('layers', []):
                for feature in layer.get('featureSet', {}).get('features', []):
                    attributes = feature.get('attributes', {})
                    geometry = feature.get('geometry', {})
                    # Check if the Route is "Gold Line (USM)"
                    if attributes.get('Route', '') == 'Gold Line (USM)':
                        # Convert coordinates and create a bus stop dictionary
                        bus_stop = {
                            'x': convert_coordinates(0, geometry.get('y'))[0],#Reversed as the x and y are reversed in the json file
                            'y': convert_coordinates(geometry.get('x'), 0)[1],
                            'location': attributes.get('Location', 'Unknown'),
                            'direction': attributes.get('Direction', 'Unknown'),
                        }
                        # Add the bus stop to the list
                        bus_stops.append(bus_stop)
```

#### The `convert_coordinates()` function

Most of the route data, coordinates seemed to be stored in EPSG:3857 format. Thus i utilized the Transformer module inside pyproj library.
Below is a basic implementation of the conversion.

```python
def convert_coordinates(x, y):
    transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
    return transformer.transform(x, y)

```

### Bus Location Fetching

#### `getCurrentLocation.py`

This script fetches the current location of a bus based on its device ID which was mapped as per data from getDataFromArcGIS.py

```python
    def get_bus_location(self, device_id):
        features = self.feature_layer.query(where=f"device_id='{device_id}'").features
        if features:
            geometry = features[0].geometry
            return geometry['y'], geometry['x']
        return None

```

### ETA Calculation

#### `getFwdAndRevEta.py`

This file contains the implementation of the `calculate_eta()` , `calculate_eta_with_waypoint_limt()`, `calculate_bus_eta()` function, which calculates the estimated time of arrival (ETA) for a bus based on the user's location and the bus's location.

The `calculate_eta_with_waypoint_limit()` function

- Calculates the ETA using waypoints, accounting for the Google Maps API limit of 25 waypoints per request.
- Handles larger chunks by splitting the waypoints into manageable segments.

```python
def calculate_eta_with_waypoint_limit(current_location, destination, waypoints):
    # If waypoints are fewer than 25, we can calculate in one call
    if len(waypoints) <= 25:
        eta = calculate_eta(current_location, destination, waypoints)
        return eta / 60  # Return ETA in minutes

    # Otherwise, split into batches of 25
    while waypoints:
        segment_waypoints = waypoints[:25]
        print(f"Calculating ETA for segment: {segment_waypoints}")
        eta_segment = calculate_eta(current_location, segment_waypoints[-1], segment_waypoints)
        print(f"ETA for segment: {eta_segment}")
        eta += eta_segment
        current_location = segment_waypoints[-1]
        waypoints = waypoints[25:]

    # Add the final leg from the last waypoint to the destination
    if waypoints:  # Only do this if there are remaining waypoints
        eta_final_leg = calculate_eta(current_location, destination, [])
        print(f"ETA for final leg: {eta_final_leg}")
        eta += eta_final_leg

    return eta / 60  # Return ETA in minutes
```

The `calculate_bus_eta()` function

- Hanldes the final ETA with the required waypoints to be traced by bus to reach the user.

```python
def calculate_bus_eta(user_location, bus_location, stops):
    # Convert stops to waypoints (latitude, longitude)
    waypoints = [(stop["x"], stop["y"]) for stop in stops]
    # Create a mapping from coordinates to stop IDs
    coord_to_stop_id = {(stop["x"], stop["y"]): stop["stop_id"] for stop in stops}

    # Find the index of the nearest stops in the waypoints list
    user_stop_index = waypoints.index([(stop["x"], stop["y"]) for stop in stops if stop["stop_id"] == nearest_stop_to_user][0])
    nearest_stop_to_bus_index = waypoints.index([(stop["x"], stop["y"]) for stop in stops if stop["stop_id"] == nearest_stop_to_bus][0])

    # Determine if the bus needs to take the reverse route
    if nearest_stop_to_bus_index > user_stop_index:
        # Calculate reverse waypoints and ETA
        reverse_waypoints = waypoints[nearest_stop_to_bus_index:] + waypoints[:user_stop_index + 1]
        reverse_eta = calculate_eta_with_waypoint_limit(bus_location, reverse_waypoints[0], reverse_waypoints)
        print(f"Reverse Stop IDs: {[coord_to_stop_id[coord] for coord in reverse_waypoints]}")
        print(f"Reverse ETA: {reverse_eta}")
        return reverse_eta
    else:
        # Calculate forward waypoints and ETA
        forward_waypoints = waypoints[nearest_stop_to_bus_index:user_stop_index + 1]
        forward_eta = calculate_eta_with_waypoint_limit(bus_location, forward_waypoints[-1], forward_waypoints)
        print(f"Forward Stop IDs: {[coord_to_stop_id[coord] for coord in forward_waypoints]}")
        print(f"Forward ETA: {forward_eta}")
        return forward_eta


```

### Frontend

The frontend is pretty self-explanatory. It is responsible for rendering the map and interacting with backend API to fetch and display bus locations, routes and ETAs.

Map Initialization

```javascript
var map = L.map("map").setView([31.3271, -89.2903], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
}).addTo(map);
```

Gets updated bus location

```javascript
function updateBusLocation() {
  fetch("/bus_location")
    .then((response) => response.json())
    .then((data) => {
      var location = data.location;
      if (location[0] && location[1]) {
        busMarker.setLatLng([location[0], location[1]]);
        busMarker.bindTooltip("Bus: " + data.bus_id);
      }
    });
}
```

Process Stops and Routes

```javascript
fetch("/bus_stops")
  .then((response) => response.json())
  .then((data) => {
    data.blue_stops.forEach((stop) => {
      L.marker([stop.x, stop.y])
        .addTo(busStopLayers["Blue Route Stops"])
        .bindPopup(`${stop.location}: ${stop.stop_id}`);
    });
  })
  .catch((error) => console.error("Error fetching bus stops: ", error));
```

```javascript
fetch("/routes")
  .then((response) => response.json())
  .then((data) => {
    var blueRoute = L.polyline(data.blue_route, {
      color: "#486dff",
      weight: 5.0,
    });
  })
  .catch((error) => console.error("Error fetching routes:", error));
```

### Flask Endpoints 
**API Endpoints**:

   - **`/track_bus`**:
     - Accepts POST and GET requests.
     - POST: Updates the bus to track based on the data received from the front end.
     - GET: Returns the current bus being tracked.

   - **`/`**:
     - Renders the main map page.

   - **`/bus_location`**:
     - Returns the current location of the bus and the bus ID.

   - **`/my_icon.png`**:
     - Serves the static icon file.

   - **`/routes`**:
     - Returns the routes for all buses in JSON format.

   - **`/bus_stops`**:
     - Returns the bus stops for the Blue, Green, and Gold routes in JSON format.

   - **`/user_location`**:
     - Accepts POST requests to update the user's location.
     - Stores the user's latitude and longitude in a global variable `user_location_data`.

   - **`/get_eta`**:
     - Accepts GET requests to calculate the ETA for the bus based on the user's location and the bus's location.
     - Uses the `calculate_bus_eta` function from `getFwdAndRevEta.py` to compute the ETA.
     - Returns the ETA in JSON format.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---



