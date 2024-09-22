from flask import Flask, render_template, jsonify
from apscheduler.schedulers.background import BackgroundScheduler
from getCurrentLocation import DeviceLocationFetcher, get_user_eta
from routesForFlask import Routes
from deviceIDs import device_id
from getDataFromArcGIS import getDataFromArcGIS
import requests

app = Flask(__name__)

# Global variable to store the current location of the bus
current_location = [31.3271, -89.2903]  # Default Hattiesburg location
feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
fetcher = DeviceLocationFetcher(feature_layer_url)


def fetch_bus_location():
    global current_location
    # device_id = "07EF9193-D679-4B84-9005-9FA2D2D1D3B5"
    location = fetcher.get_device_location(device_id["blue1"])
    if location:
        current_location = location

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


@app.route('/get_eta', methods=['POST'])
def calculate_eta():
    user_lat = request.json.get('user_lat')
    user_lng = request.json.get('user_lng')
    
    # Destination coordinates (for example, a bus stop or a fixed location)
    dest_lat = 31.3300  # Replace with your destination's latitude
    dest_lng = -89.2900  # Replace with your destination's longitude

    # Call the function to get ETA
    distance, duration = get_user_eta(user_lat, user_lng, dest_lat, dest_lng)

    if distance and duration:
        return jsonify({
            'distance': distance,
            'duration': duration
        })
    else:
        return jsonify({'error': 'Unable to calculate ETA'}), 500



# Background scheduler to fetch bus location every 5 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_bus_location, trigger="interval", seconds=5)
scheduler.start()

# Initialize route data when the app starts
if __name__ == "__main__":
    fetch_bus_location()  # Fetch initial bus location
    app.run(debug=True, use_reloader=False)
# from flask import Flask, render_template, jsonify
# from apscheduler.schedulers.background import BackgroundScheduler
# from getCurrentLocation import DeviceLocationFetcher

# app = Flask(__name__)

# # Initialize the DeviceLocationFetcher
# feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
# fetcher = DeviceLocationFetcher(feature_layer_url)

# # Global variable to store the bus location
# bus_location = {"latitude": None, "longitude": None}

# def fetch_bus_location():
#     global bus_location
#     device_id = "07EF9193-D679-4B84-9005-9FA2D2D1D3B5"
#     location = fetcher.get_device_location(device_id)
#     if location:
#         bus_location["latitude"], bus_location["longitude"] = location

# # Background scheduler to fetch bus location every 5 seconds
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=fetch_bus_location, trigger="interval", seconds=5)
# scheduler.start()

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/bus_location")
# def get_bus_location():
#     return jsonify(bus_location)

# # Initialize route data when the app starts
# if __name__ == "__main__":
#     fetch_bus_location()  # Fetch initial bus location
#     app.run(debug=True, use_reloader=False)
