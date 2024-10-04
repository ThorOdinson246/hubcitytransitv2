import googlemaps
from datetime import datetime
import numpy as np

API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'

gmaps = googlemaps.Client(key=API_KEY)


def calculate_bus_eta(user_location_data, current_location, blue_route_converted_stops):
    # Convert user_location_data and current_location to tuples
    user_location = (user_location_data['lat'], user_location_data['lng'])
    bus_location = (current_location[0], current_location[1])

    # Extract coordinates from blue_route_converted_stops
    bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

    # Find the nearest stop to the bus
    nearest_stop = find_nearest_stop(user_location, bus_stops)

    # Find the index of the nearest stop
    nearest_stop_index = bus_stops.index(nearest_stop)

    # Prepare waypoints for the API call
    waypoints = bus_stops[nearest_stop_index:]

    # Calculate the route from the bus to the nearest stop
    bus_to_stop_route = gmaps.directions(
        bus_location,
        nearest_stop,
        waypoints=waypoints,
        optimize_waypoints=False,
        mode="driving",
        departure_time=datetime.now()
    )

    # Extract the ETA
    if bus_to_stop_route:
        # eta_seconds = bus_to_stop_route[0]['legs'][-1]['duration']['value']
        # eta_minutes = eta_seconds // 60
        total_duration = sum(leg['duration']['value']
                             for leg in bus_to_stop_route[0]['legs'])
        eta_minutes = total_duration // 60
        nearest_stop_info = blue_route_converted_stops[nearest_stop_index]['location']
        return nearest_stop_info, eta_minutes
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

# Example usage (you would call this function after fetching the required data)


def get_bus_eta():
    from app import current_location, blue_route_converted_stops
    user_location_data = {'lat': 31.325444, 'lng': -89.348104}

    if user_location_data['lat'] is None or user_location_data['lng'] is None:
        return {"error": "User location not available"}

    if not current_location:
        return {"error": "Bus location not available"}
    else:
        print(f"Bus location: {current_location}")
    nearest_stop, eta = calculate_bus_eta(
        user_location_data, current_location, blue_route_converted_stops)

    if nearest_stop and eta:
        return {
            "nearest_stop": nearest_stop,
            "eta_minutes": eta
        }
    else:
        return {"error": "Unable to calculate ETA"}

# Test the function


print(get_bus_eta())
