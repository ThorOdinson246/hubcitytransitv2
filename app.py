from flask import Flask, render_template, jsonify, request
from apscheduler.schedulers.background import BackgroundScheduler
from getCurrentLocation import DeviceLocationFetcher, get_user_eta
from routesForFlask import Routes
from deviceIDs import device_id
from getDataFromArcGIS import getDataFromArcGIS

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

# COMMENT C# STARTS HERE 
# 
@app.route('/get_eta', methods=['POST'])
def calculate_eta():
    user_lat = request.json.get('user_lat')
    user_lng = request.json.get('user_lng')
    
    # Destination coordinates (for example, a bus stop or a fixed location)
    dest_lat = 31.324767  # Replace with your destination's latitude
    dest_lng = -89.306918  # Replace with your destination's longitude

    # Call the function to get ETA
    distance, duration = get_user_eta(user_lat, user_lng, dest_lat, dest_lng)

    if distance and duration:
        return jsonify({
            'distance': distance,
            'duration': duration
        })
    else:
        return jsonify({'error': 'Unable to calculate ETA'}), 500

# COMMENT C# ENDS HERE

# get user location from the front end and calculate the ETA
@app.route('/user_location', methods=['POST'])
def user_location_and_calc_eta():
    user_lat = request.json.get('user_lat')
    user_lng = request.json.get('user_lng')
    if(user_lat and user_lng):
        print("Data received from the front end")
    else: 
        print("Data not yet received from the front end")
    return jsonify({'user_location': [user_lat, user_lng]})

# Background scheduler to fetch bus location every 5 seconds
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_bus_location, trigger="interval", seconds=5)
scheduler.start()

# Initialize route data when the app starts
if __name__ == "__main__":
    fetch_bus_location()  # Fetch initial bus location

    # 
    app.run(debug=True, use_reloader=False)
