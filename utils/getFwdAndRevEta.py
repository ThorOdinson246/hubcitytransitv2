# Use Google Maps API to calculate ETA, once the shortest route i.e the route forward, and then the reverse route, just go through that route in reverse order
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from extracted_stops import blue_route_converted_stops
from getCurrentLocation import DeviceLocationFetcher
from utils.deviceIDs import device_id

API_KEY = "AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ"

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
    for stop in blue_route_converted_stops:
        stop_lat = stop['x']
        stop_lng = stop['y']
        distance = haversine(user_lat, user_lng, stop_lat, stop_lng)
        if distance < min_distance:
            min_distance = distance
            nearest_stop = stop['stop_id']
    return nearest_stop

def get_bus_location_by_id(bus_id):
    location=DeviceLocationFetcher("https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1")
    bus_lat = location.get_bus_location(device_id[bus_id])[0]
    bus_lng = location.get_bus_location(device_id[bus_id])[1]
    return bus_lat, bus_lng

# Calculate ETA with waypoint limit (improved)
def calculate_eta_with_waypoint_limit(current_location, destination, waypoints):
    eta = 0
    while waypoints:
        segment_waypoints = waypoints[:25]
        # print(f"Calculating ETA for segment: {segment_waypoints}")  # Debugging statement
        eta_segment = calculate_eta(current_location, segment_waypoints[-1], segment_waypoints)
        print(f"ETA for segment: {eta_segment}")  # Debugging statement
        eta += eta_segment
        current_location = segment_waypoints[-1]
        waypoints = waypoints[25:]
    # Add the final leg from the last waypoint to the destination
    eta_final_leg = calculate_eta(current_location, destination, [])
    print(f"ETA for final leg: {eta_final_leg}")  # Debugging statement
    eta += eta_final_leg
    # return eta in minutes,
    return eta/60

# Calculate ETA (improved)
def calculate_eta(current_location, destination, waypoints):
    base_url = "https://maps.googleapis.com/maps/api/directions/json"
    params = {
        "origin": f"{current_location[0]},{current_location[1]}",
        "destination": f"{destination[0]},{destination[1]}",
        "waypoints": "|".join(f"{lat},{lng}" for lat, lng in waypoints),
        "mode": "driving",
        "key": API_KEY,
    }

    # print("Request parameters:", params)  # Debugging statement

    response = requests.get(base_url, params=params)
    data = response.json()

    # print("API response:", data)  # Debugging statement

    if data["status"] == "OK":
        return data["routes"][0]["legs"][0]["duration"]["value"]
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

if __name__ == "__main__":
     # Example user location (latitude, longitude)
    user_location = (31.325961, -89.338733)
    print(f"User location: {user_location}")  # Debugging statement
    bus_location = (31.326095, -89.377890)

    waypoints=[(stop["x"], stop["y"]) for stop in blue_route_converted_stops]

    nearest_stop_to_user = get_nearest_stop(user_location[0], user_location[1])
    print(f"Nearest stop to user index: {nearest_stop_to_user}")  # Debugging statement
    nearest_stop_to_bus = get_nearest_stop(bus_location[0], bus_location[1])
    print(f"Nearest stop to bus: {nearest_stop_to_bus}")  # Debugging statement

    # Find indices of nearest stops
    user_stop_index = waypoints.index([(stop["x"], stop["y"]) for stop in blue_route_converted_stops if stop["stop_id"] == nearest_stop_to_user][0])
    nearest_stop_to_bus_index = waypoints.index([(stop["x"], stop["y"]) for stop in blue_route_converted_stops if stop["stop_id"] == nearest_stop_to_bus][0])


# Stop id printing for better understanding 
    coord_to_stop_id = {(stop["x"], stop["y"]): stop["stop_id"] for stop in blue_route_converted_stops}


    # Determine the direction of travel
    if nearest_stop_to_bus_index > user_stop_index:
        # Bus has already passed the user
        direction = "reverse"
        forward_waypoints = waypoints[user_stop_index:nearest_stop_to_bus_index + 1]
        # Stop id printing for better understanding 

        forward_stop_ids = [coord_to_stop_id[coord] for coord in forward_waypoints]
        print(f"Forward stop IDs: {forward_stop_ids}")  # Debugging statement


        reverse_waypoints = waypoints[:user_stop_index][::-1] + forward_waypoints
        
        
        reverse_stop_ids = [coord_to_stop_id[coord] for coord in reverse_waypoints]
        print(f"Reverse stop IDs: {reverse_stop_ids}")  # Debugging statement

        print(f"Reverse waypoints: {reverse_waypoints}") 
        print(f"Forward waypoints: {forward_waypoints}")
    else:
        # Bus is yet to come
        direction = "forward"
        forward_waypoints = waypoints[user_stop_index:nearest_stop_to_bus_index + 1]
        
        
        forward_stop_ids = [coord_to_stop_id[coord] for coord in forward_waypoints]
        print(f"Forward stop IDs: {forward_stop_ids}")  # Debugging statement


        reverse_waypoints = waypoints[nearest_stop_to_bus_index:][::-1]
        

        reverse_stop_ids = [coord_to_stop_id[coord] for coord in reverse_waypoints]
        print(f"Reverse stop IDs: {reverse_stop_ids}")  # Debugging statement

        
        print(f"Forward waypoints: {forward_waypoints}")
        print(f"Reverse waypoints: {reverse_waypoints}")
    print("Direction is actually ", direction)
    forward_eta = calculate_eta_with_waypoint_limit(bus_location, forward_waypoints[-1], forward_waypoints)
    print( "Shortest route is forward with ETA:", forward_eta)

    reverse_eta = calculate_eta_with_waypoint_limit(bus_location, reverse_waypoints[0], reverse_waypoints)
    print( "Shortest route is reverse with ETA:", reverse_eta)
    








# # WORKING LOGIC BU ERROR IN INDEXXXX .
#     # Get nearest stop to user location
#     nearest_stop_to_user = get_nearest_stop(user_location[0], user_location[1])
#     print(f"Nearest stop to user: {nearest_stop_to_user}")  # Debugging statement

#     # Get bus location
#     # bus_location = get_bus_location_by_id("blue1")
#     bus_location = (31.324849, -89.334886)
#     print(f"Bus location: {bus_location}")  # Debugging statement

#     nearest_stop_to_bus = get_nearest_stop(bus_location[0], bus_location[1])
#     print(f"Nearest stop to bus: {nearest_stop_to_bus}")  # Debugging statement

#     waypoints = [(stop["x"], stop["y"]) for stop in blue_route_converted_stops]

#     # Find the index of the nearest stop to the bus
#     nearest_stop_to_bus_index = waypoints.index([(stop["x"], stop["y"]) for stop in blue_route_converted_stops if stop["stop_id"] == nearest_stop_to_bus][0])
#     print(f"Nearest stop to bus index: {nearest_stop_to_bus_index}")  # Debugging statement

#     # Identify relevant waypoints for forward ETA
#     user_stop_index = waypoints.index([(stop["x"], stop["y"]) for stop in blue_route_converted_stops if stop["stop_id"] == nearest_stop_to_user][0])
#     forward_waypoints = waypoints[user_stop_index:nearest_stop_to_bus_index + 1]  # Include both start and end stops
#     print(f"Forward waypoints: {forward_waypoints}")  # Debugging statement

#     # Calculate forward ETA
#     forward_eta = calculate_eta_with_waypoint_limit(bus_location, forward_waypoints[-1], forward_waypoints)
#     print(f"Forward ETA: {forward_eta}")  # Debugging statement

#     # Identify relevant waypoints for reverse ETA
#     reverse_waypoints = waypoints[:user_stop_index][::-1] + waypoints[nearest_stop_to_bus_index:]  # Include the entire reverse route
#     print(f"Reverse waypoints: {reverse_waypoints}")  # Debugging statement

#     # Calculate reverse ETA
#     reverse_eta = calculate_eta_with_waypoint_limit(bus_location, reverse_waypoints[0], reverse_waypoints)
#     print(f"Reverse ETA: {reverse_eta}")  # Debugging statement

#     # Determine the shortest route and ETA
#     if forward_eta < reverse_eta:
#         print("Shortest route is forward with ETA:", forward_eta)
#     else:
#         print("Shortest route is reverse with ETA:", reverse_eta)# Commented cuz better do this in frontend 
