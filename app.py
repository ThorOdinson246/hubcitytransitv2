from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from utils.getCurrentLocation import DeviceLocationFetcher, get_user_eta
from utils.routesForFlask import Routes
from utils.deviceIDs import device_id
from utils.getDataFromArcGIS import getDataFromArcGIS
import requests
from routesAndStops.extracted_stops import blue_route_converted_stops

app = Flask(__name__)

# Global variable to store the current location of the bus
current_location = [31.3271, -89.2903]  # Default Hattiesburg location
feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
fetcher = DeviceLocationFetcher(feature_layer_url)


def fetch_bus_location():
    global current_location
    # device_id = "07EF9193-D679-4B84-9005-9FA2D2D1D3B5"
    location = fetcher.get_bus_location(device_id["blue1"])
    if location:
        current_location = location
        print("Bus location debug:", current_location)

@app.route('/')
def index():
    return render_template('map.html')

@app.route('/bus_location')
def bus_location():
    return jsonify({'location': current_location})

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
    blue_route_stops_data = blue_route_converted_stops
    return jsonify(blue_route_converted_stops)
    


# COMMENT C# STARTS HERE 
# # 
# @app.route('/get_eta', methods=['POST'])
# def calculate_eta():
#     user_lat = request.json.get('user_lat')
#     user_lng = request.json.get('user_lng')
#     # GEt destination coordinates from return value of user_location_and_calc_eta
#     # dest_lat = 
#     dest_lng = -89.306918  # Replace with your destination's longitude

#     # Call the function to get ETA
#     distance, duration = get_user_eta(user_lat, user_lng, dest_lat, dest_lng)

#     if distance and duration:
#         return jsonify({
#             'distance': distance,
#             'duration': duration
#         })
#     else:
#         return jsonify({'error': 'Unable to calculate ETA'}), 500

# COMMENT C# ENDS HERE

# Store user location in a global variable
user_location_data = {'lat': None, 'lng': None}

@app.route('/user_location', methods=['POST'])
def user_location():
    global user_location_data
    user_lat = request.json.get('user_lat')
    user_lng = request.json.get('user_lng')
    if user_lat and user_lng:
        user_location_data = {'lat': user_lat, 'lng': user_lng}
        print("User location data received:", user_location_data)
        return jsonify({"status": "success", "message": "Location received"})
    else:
        print("Invalid user location data")
        return jsonify({"status": "error", "message": "Invalid location data"}), 400

@app.route('/get_eta', methods=['GET'])
def get_eta():
    dest_lat = current_location[0]
    dest_lng = current_location[1]

    user_lat = user_location_data['lat']
    user_lng = user_location_data['lng']

    if user_lat is None or user_lng is None:
        return jsonify({"status": "error", "message": "User location not set"}), 400
    else:
        print(f"Data is received , now computing the ETA between user : {user_lat},{user_lng} and destination: {dest_lat},{dest_lng}")

    distance,duration=get_user_eta(user_lat, user_lng, dest_lat, dest_lng)

    return jsonify({
        'distance': distance,
        'eta': duration
    })


# Background scheduler to fetch bus location every 5 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_bus_location, trigger="interval", seconds=5)
scheduler.start()

# Initialize route data when the app starts
if __name__ == "__main__":
    fetch_bus_location()  # Fetch initial bus location

    # 
    app.run(debug=True, use_reloader=False)
