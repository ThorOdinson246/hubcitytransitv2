# import os
# import sys

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from utils.extracted_stops import blue_route_converted_stops
from utils.getCurrentLocation import DeviceLocationFetcher
from utils.deviceIDs import device_id
from utils.state_manager import bus_state
from apis import MY_GMAPS_API, FEATURE_LAYER_URL

API_KEY = MY_GMAPS_API

# GET THE NEAREST STOP TO USER LOCATION fROM BLUE_ROUTE_CONVERTED_STOPS
def haversine(lat1, lon1, lat2, lon2):
    from math import radians, sin, cos, asin, sqrt

    # Convert latitude and longitude to radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculate the Haversine distance
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of Earth in kilometers
    return c * r  * 1000  # Convert to meters

# Get the nearest stop to the user's location
def get_nearest_stop(user_lat, user_lng):
    nearest_stop = None
    min_distance = float('inf')
    from app import get_tracking_route
    route_stops=get_tracking_route(bus_state.current_bus)
    for stop in route_stops:
        stop_lat = stop['x']
        stop_lng = stop['y']
        distance = haversine(user_lat, user_lng, stop_lat, stop_lng)
        if distance < min_distance:
            min_distance = distance
            nearest_stop = stop['stop_id']
    return nearest_stop

def get_bus_location_by_id(bus_id):
    location=DeviceLocationFetcher(FEATURE_LAYER_URL)
    bus_lat = location.get_bus_location(device_id[bus_id])[0]
    bus_lng = location.get_bus_location(device_id[bus_id])[1]
    return bus_lat, bus_lng

# Calculate ETA with waypoint limit (improved)
def calculate_eta_with_waypoint_limit(current_location, destination, waypoints):
    eta = 0
    
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

# Calculate ETA (improved)
def calculate_eta(current_location, destination, waypoints):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{current_location[0]},{current_location[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "waypoints": "|".join(f"{lat},{lng}" for lat, lng in waypoints),  
        "mode": "driving",
        "key": API_KEY,
        "departure_time": "now",
        "traffic_model": "optimistic",
        'optimize_waypoints': 'false'
    }

    print("PAISA UTHYOOOOOOOOOOOOOO")   

    response = requests.get(base_url, params=params)
    data = response.json()

    if data["status"] == "OK":
        # mya chicken bug ho ki k ho, but direct legs ko total duration ligda, sab route ko follow nai garena,so manually add handiye legs ko eta  
        #also mya chicken, segmentation nahuda, ra reverse logic follow garnu parda, last leg le, reverse ta xadai xa, but arko sida wala ni jodi rathyo 
        total_duration = 0
        legs = data["routes"][0]["legs"]
        # Exclude the last leg from the total duration
        for leg in legs[:-1]:
            total_duration += leg["duration"]["value"]
        return total_duration
        # return data["routes"][0]["legs"][0]["duration"]["value"]
    else:
        print("Error in Fetching Data , Status: ", data["status"])
        return None

# Get the index of the current stop
def get_current_stop_index(bus_location, waypoints):
    min_distance = float('inf')
    nearest_stop_index = None
    for i, (lat, lng) in enumerate(waypoints):
        distance = haversine(bus_location[0], bus_location[1], lat, lng)
        if distance < min_distance:
            min_distance = distance
            nearest_stop_index = i
    return nearest_stop_index

# Get the reverse route waypoints
def get_reverse_route_waypoints(waypoints, current_stop_index):
    return waypoints[:current_stop_index][::-1]

# Main logic to calculate BUS ETA 
def calculate_bus_eta(user_location, bus_location, stops):
    # Convert stops to waypoints (latitude, longitude)
    waypoints = [(stop["x"], stop["y"]) for stop in stops]
    # Create a mapping from coordinates to stop IDs
    coord_to_stop_id = {(stop["x"], stop["y"]): stop["stop_id"] for stop in stops}

    # Get the nearest stop to the user and the bus
    nearest_stop_to_user = get_nearest_stop(user_location[0], user_location[1])
    nearest_stop_to_bus = get_nearest_stop(bus_location[0], bus_location[1])

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


# Example usage
if __name__ == "__main__":
     # Example user location (latitude, longitude)
    user_location = (31.325533, -89.338932)
    bus_location = (31.325789, -89.373866

)
    eta = calculate_bus_eta(user_location, bus_location, blue_route_converted_stops)
    print(f"Final ETA: {eta} minutes")


