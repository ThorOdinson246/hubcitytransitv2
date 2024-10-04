# Collection of waypoints for the blue route of the bus in order so, that calculation of ETA will be done with waypoints in mind.
# If a user is at a location, the nearest bus stop will be found and the ETA will be calculated with the bus stop as the starting point.
# But if the buss passes the user, It will calculate ETa with consideration that bus cannot go back to the user location but have to complete and entre route and then come back to the user location.


# Get waypoints from the blue route
# Waypoints are the coordinates of the bus stops on the route

import requests

# Your Google Maps API key
API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'

import googlemaps
from datetime import datetime
import numpy as np

# Initialize the Google Maps client
gmaps = googlemaps.Client(key='YOUR_API_KEY')

def calculate_bus_eta(user_location, bus_location, bus_stops):
    # Find the nearest stop to the bus
    nearest_stop = find_nearest_stop(bus_location, bus_stops)
    
    # Calculate the route from the bus to the nearest stop
    bus_to_stop_route = gmaps.directions(
        bus_location,
        nearest_stop,
        waypoints=bus_stops[bus_stops.index(nearest_stop):],
        optimize_waypoints=False,
        mode="driving",
        departure_time=datetime.now()
    )
    
    # Extract the ETA
    if bus_to_stop_route:
        eta_seconds = bus_to_stop_route[0]['legs'][-1]['duration']['value']
        eta_minutes = eta_seconds // 60
        return nearest_stop, eta_minutes
    else:
        return None, None

def find_nearest_stop(location, stops):
    # Convert stops to numpy array for efficient calculation
    stops_array = np.array(stops)
    location_array = np.array(location)
    
    # Calculate distances
    distances = np.sum((stops_array - location_array) ** 2, axis=1)
    
    # Find index of minimum distance
    nearest_index = np.argmin(distances)
    
    return tuple(stops_array[nearest_index])

# Example usage
user_location = (37.7749, -122.4194)  # San Francisco
bus_location = (37.7833, -122.4167)  # Example bus location
bus_stops = [
    (37.7855, -122.4001),  # Stop 1
    (37.7897, -122.3887),  # Stop 2
    (37.7946, -122.3943),  # Stop 3
    # Add more stops as needed
]

nearest_stop, eta = calculate_bus_eta(user_location, bus_location, bus_stops)

if nearest_stop and eta:
    print(f"The nearest stop to the bus is at {nearest_stop}")
    print(f"The estimated time of arrival is {eta} minutes")
else:
    print("Unable to calculate ETA")