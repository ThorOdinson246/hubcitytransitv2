from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils.getCurrentLocation import DeviceLocationFetcher, get_user_eta
from utils.routesForFlask import Routes
from utils.deviceIDs import device_id
from utils.extracted_stops import blue_route_converted_stops, green_route_converted_stops, gold_route_converted_stops
from utils.state_manager import *
from apis import *

app = Flask(__name__)

# Global variable to store the current location of the bus
current_location =31.324811, -89.328526

#Change location here to test  location of the bus
feature_layer_url=FEATURE_LAYER_URL
fetcher = DeviceLocationFetcher(feature_layer_url)
global bus_to_track
bus_to_track = "blue1"

def fetch_bus_location():
    global current_location
    location = fetcher.get_bus_location(device_id[bus_state.current_bus])
    if location:
        current_location = location
        return current_location, bus_state.current_bus #the bus_state.current_bus is only for testing purposes 

@app.route('/track_bus', methods=['POST', 'GET'])
def track_bus():
    # global bus_to_track
    if request.method == 'POST':
        data = request.get_json()
        bus_state.current_bus = data.get('bus_to_track', 'blue1')
        bus_to_track = data.get('bus_to_track', 'blue1')  # Default to blue1 if not provided
        print("From front end, bus to track:", bus_state.current_bus)
        return jsonify({
            "status": "success", 
            "bus_to_track": bus_state.current_bus,
            "message": f"Now tracking {bus_state.current_bus}"
        })
    elif request.method == 'GET':
        return jsonify({
            "status": "success",
            "bus_to_track": bus_state.current_bus,
            "message": f"Currently tracking {bus_state.current_bus}"
        })

def get_tracking_route(bus_to_track=None): 
    # global bus_to_track
    if bus_to_track is None:
        bus_to_track = bus_state.current_bus
    print("For the function get_tracking_route, bus to track:", bus_to_track)
    if bus_to_track=="blue1" or bus_to_track=="blue2":
        return blue_route_converted_stops
    elif bus_to_track=="gold1" or bus_to_track=="gold2":
        return gold_route_converted_stops
    elif bus_to_track=="green":
        return green_route_converted_stops
    else:
        print("Bus not found, going with default route: blue")
        return blue_route_converted_stops

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/bus_location')
def bus_location():
    return jsonify({'location': fetch_bus_location()[0], 'bus_id': fetch_bus_location()[1]})

@app.route('/my_icon.png')
def icon():
    return app.send_static_file('my_icon.png')

@app.route('/routes')
def get_routes():
    routes = {
        "blue_route": Routes.convert_coordinates(Routes.get_blue_route()),
        "gold_route": Routes.convert_coordinates(Routes.get_gold_route()),
        "green_route": Routes.convert_coordinates(Routes.get_green_route()),
        "brown_route": Routes.convert_coordinates(Routes.get_brown_route()),
        "orange_route": Routes.convert_coordinates(Routes.get_orange_route()),
        "red_route": Routes.convert_coordinates(Routes.get_red_route()),
        "purple_route": Routes.convert_coordinates(Routes.get_purple_route()),
    }
    return jsonify(routes)

@app.route('/bus_stops')
def get_bus_stops():
    bus_stops={
        "blue_stops": blue_route_converted_stops,
        "green_stops": green_route_converted_stops,
        "gold_stops": gold_route_converted_stops

    }
    return jsonify(bus_stops)
    

# Store user location in a global variable
user_location_data = {'lat': None, 'lng': None}

@app.route('/user_location', methods=['POST'])
def user_location():
    global user_location_data
    # global which_bus
    user_lat = request.json.get('user_lat')
    user_lng = request.json.get('user_lng')
    if user_lat and user_lng:
        user_location_data = {'lat': user_lat, 'lng': user_lng}
        print("User location data received:", user_location_data)
        return jsonify({"status": "success", "message": "Location received"})
    else:
        print("Invalid user location data")
        return jsonify({"status": "error", "message": "Invalid location data"}), 400
  
from utils.getFwdAndRevEta import calculate_bus_eta
@app.route('/get_eta', methods=['GET'])
def get_eta():
    # global bus_to_track
    current_bus = bus_state.current_bus
    # print(which_bus)
    print("Current bus to track for get_eta:", current_bus)
    try:
        dest_lat = current_location[0]
        dest_lng = current_location[1]

        user_lat = user_location_data.get('lat')
        user_lng = user_location_data.get('lng')

        if user_lat is None or user_lng is None:
            return jsonify({
                "status": "error", 
                "message": "User location not set",
                "eta": None
            })

        print(f"Computing ETA for {current_bus} between user: {user_lat},{user_lng} and destination: {dest_lat},{dest_lng}")
        route= get_tracking_route(current_bus)
        eta = calculate_bus_eta(
            (user_lat, user_lng), 
            (dest_lat, dest_lng), 
            route
        )
        
        return jsonify({
            'status': 'success',
            'eta': eta,
            'bus_tracking': current_bus
        })
        
    except Exception as e:
        print(f"Error calculating ETA: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'eta': None
        })


# Background scheduler to fetch bus location every 5 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_bus_location, trigger="interval", seconds=5)
scheduler.start()

# Initialize route data when the app starts
if __name__ == "__main__":
    fetch_bus_location()  # Fetch initial bus location
    app.run(debug=True, host='0.0.0.0', port=5000)


