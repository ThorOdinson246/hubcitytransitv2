import folium

# Example usage for visualization

from app import current_location, blue_route_converted_stops
import googlemaps
from datetime import datetime
import numpy as np
from itertools import islice


API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'

gmaps = googlemaps.Client(key=API_KEY)


# def calculate_bus_eta(user_location_data, current_location, blue_route_converted_stops):
#     # Convert user_location_data and current_location to tuples
#     user_location = (user_location_data['lat'], user_location_data['lng'])
#     bus_location = (current_location[0], current_location[1])

#     # Extract coordinates from blue_route_converted_stops
#     bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

#     # Find the nearest stop to the bus
#     nearest_stop = find_nearest_stop(user_location, bus_stops)

#     # Find the index of the nearest stop
#     nearest_stop_index = bus_stops.index(nearest_stop)

#     # Prepare waypoints for the API call
#     waypoints = bus_stops[nearest_stop_index:]

#     # Calculate the route from the bus to the nearest stop
#     bus_to_stop_route = gmaps.directions(
#         bus_location,
#         nearest_stop,
#         waypoints=waypoints,
#         optimize_waypoints=False,
#         mode="driving",
#         traffic_model="optimistic",
#         departure_time=datetime.now()
#     )

#     # Extract the ETA
#     if bus_to_stop_route:
#         # eta_seconds = bus_to_stop_route[0]['legs'][-1]['duration']['value']
#         # eta_minutes = eta_seconds // 60
#         total_duration = sum(leg['duration']['value']
#                              for leg in bus_to_stop_route[0]['legs'])
#         eta_minutes = total_duration // 60
#         nearest_stop_info = blue_route_converted_stops[nearest_stop_index]['location']
#         return nearest_stop_info, eta_minutes
#     else:
#         return None, None


# def find_nearest_stop(location, stops):
#     # Convert stops to numpy array for efficient calculation
#     stops_array = np.array(stops)
#     location_array = np.array(location)

#     # Calculate distances
#     distances = np.sum((stops_array - location_array) ** 2, axis=1)

#     # Find index of minimum distance
#     nearest_index = np.argmin(distances)

#     return tuple(stops_array[nearest_index])

# # Example usage (you would call this function after fetching the required data)


# def get_bus_eta():
#     from app import current_location, blue_route_converted_stops
#     user_location_data = {'lat': 31.325444, 'lng': -89.348104}

#     if user_location_data['lat'] is None or user_location_data['lng'] is None:
#         return {"error": "User location not available"}

#     if not current_location:
#         return {"error": "Bus location not available"}
#     else:
#         print(f"Bus location: {current_location}")
#     nearest_stop, eta = calculate_bus_eta(
#         user_location_data, current_location, blue_route_converted_stops)

#     if nearest_stop and eta:
#         return {
#             "nearest_stop": nearest_stop,
#             "eta_minutes": eta
#         }
#     else:
#         return {"error": "Unable to calculate ETA"}

# # Test the function


# print(get_bus_eta())
def calculate_bus_eta(user_location_data, current_location, blue_route_converted_stops):
    print("Start of calculate_bus_eta function")
    
    # User and bus location
    user_location = (user_location_data['lat'], user_location_data['lng'])
    bus_location = (current_location[0], current_location[1])

    # Debugging: Print the user's and bus's location
    print(f"User location: {user_location}")
    print(f"Bus location: {bus_location}")

    # Extract coordinates for bus stops
    bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

    # Debugging: Print bus stops to ensure they're correct
    print(f"Bus stops: {bus_stops}")

    # Nearest stop to user and its index
    nearest_stop_to_user = find_nearest_stop(user_location, bus_stops)
    nearest_stop_index = bus_stops.index(nearest_stop_to_user)

    # Nearest stop to bus and its index
    nearest_stop_to_bus = find_nearest_stop(bus_location, bus_stops)
    bus_index = bus_stops.index(nearest_stop_to_bus)

    # Debugging: Print nearest stop to user and bus, along with indices
    print(f"Nearest stop to user: {nearest_stop_to_user}, Index: {nearest_stop_index}")
    print(f"Nearest stop to bus: {nearest_stop_to_bus}, Index: {bus_index}")

    print("Calculating forward ETA...")

    # Forward ETA: Bus approaching the stop
    forward_eta = calculate_direction_eta(
        bus_location, nearest_stop_to_user, blue_route_converted_stops, bus_index, nearest_stop_index)

    # Debugging: Check the value of forward ETA
    print(f"Forward ETA (approaching the stop): {forward_eta}")

    print("Calculating reverse ETA...")

    # Reverse ETA: Bus has passed the stop, needs to complete the entire route
    reverse_eta = calculate_direction_eta(
        bus_location, nearest_stop_to_user, blue_route_converted_stops[::-1], len(bus_stops) - 1 - bus_index, len(bus_stops) - 1 - nearest_stop_index)

    # Debugging: Check the value of reverse ETA
    print(f"Reverse ETA (looping around the route): {reverse_eta}")

    # Checking if both ETAs are calculated properly
    if forward_eta is not None and reverse_eta is not None:
        print("Forward and Reverse ETA calculated successfully.")
        next_arrival = min(forward_eta, reverse_eta)
        following_arrival = max(forward_eta, reverse_eta)

        nearest_stop_info = blue_route_converted_stops[nearest_stop_index]['location']
        print(f"Next arrival: {next_arrival}, Following arrival: {following_arrival}")
        return nearest_stop_info, next_arrival, following_arrival
    else:
        print("Error: Unable to calculate ETA (forward or reverse returned None)")
        return None, None, None
    
# chunks cuz google only accepts 25 waypoints at a time
def chunked_iterable(iterable, size):
    """Yield successive n-sized chunks from iterable."""
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, size))
        if not chunk:
            break
        yield chunk


def calculate_direction_eta(start_location, end_location, stops, start_index, end_index):
    if start_index <= end_index:
        waypoints = stops[start_index:end_index + 1]
    else:
        waypoints = stops[start_index:] + stops[:end_index + 1]

    # Extract coordinates for Google Maps API (ensure (lat, lon) order)
    waypoint_coords = [(stop['x'], stop['y']) for stop in waypoints]

    # Split waypoints into chunks of 25
    waypoint_chunks = list(chunked_iterable(waypoint_coords, 25))
    
    total_duration = 0
    current_origin = start_location

    for i, chunk in enumerate(waypoint_chunks):
        # Add the destination to the last chunk
        if i == len(waypoint_chunks) - 1:
            chunk = list(chunk) + [end_location]
        else:
            chunk = list(chunk)
        
        # # Debugging: Print the chunk details
        # print(f"Chunk {i}:")
        # print(f"Origin: {current_origin}")
        # print(f"Destination: {chunk[-1]}")
        # print(f"Waypoints: {chunk[:-1]}")

        # Calculate directions for the current chunk
        route = gmaps.directions(
            current_origin,
            chunk[-1],
            waypoints=chunk[:-1] if chunk[:-1] else None,
            optimize_waypoints=False,
            mode="driving",
            traffic_model="optimistic",

            departure_time=datetime.now()
        )
        
        # Sum the duration of each leg
        if route:
            total_duration += sum(leg['duration']['value'] for leg in route[0]['legs'])
        
        # Update the origin for the next chunk
        current_origin = chunk[-1]
    
    eta_minutes = total_duration // 60
    return eta_minutes

def find_nearest_stop(location, stops):
    stops_array = np.array(stops)
    location_array = np.array(location)
    distances = np.sum((stops_array - location_array) ** 2, axis=1)
    nearest_index = np.argmin(distances)
    return tuple(stops_array[nearest_index])

# # Usage example
# if user_location_data['lat'] is None or user_location_data['lng'] is None:
#     print({"error": "User location not available"})
# if not current_location:
#     print({"error": "Bus location not available"})
# else:
#     print(f"Bus location: {current_location}")

# nearest_stop, next_arrival, following_arrival = calculate_bus_eta(
#     user_location_data, current_location, blue_route_converted_stops)

# if nearest_stop and next_arrival and following_arrival:
#     print({
#         "nearest_stop to bus ": nearest_stop,
#         "next_arrival": next_arrival,
#         "following_arrival": following_arrival
#     })
# else:
#     print({"error": "Unable to calculate ETA"})


# Call the calculate_bus_eta function with the above data

def visualize_route(user_location_data, current_location, blue_route_converted_stops):
    # Calculate bus ETA as you have done before
    nearest_stop, next_arrival, following_arrival = calculate_bus_eta(
        user_location_data, current_location, blue_route_converted_stops
    )

    # Create a map centered around the user's location
    m = folium.Map(location=[user_location_data['lat'], user_location_data['lng']], zoom_start=14)

    # Add a marker for the user's location
    folium.Marker(
        location=[user_location_data['lat'], user_location_data['lng']],
        popup='User Location',
        icon=folium.Icon(color='blue')
    ).add_to(m)

    # Add a marker for the bus's current location
    folium.Marker(
        location=[current_location[0], current_location[1]],
        popup='Bus Location',
        icon=folium.Icon(color='red')
    ).add_to(m)

    # Extract coordinates for bus stops
    bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

    # Create a list of waypoints (user's nearest stop to bus location)
    nearest_stop_to_user = find_nearest_stop((user_location_data['lat'], user_location_data['lng']), bus_stops)
    nearest_stop_index = bus_stops.index(nearest_stop_to_user)

    # Add waypoints to the map
    for stop in bus_stops:
        folium.Marker(
            location=stop,
            icon=folium.Icon(color='green')
        ).add_to(m)

    # Draw the path from bus to nearest stop
    waypoints = bus_stops[nearest_stop_index:]  # Path to the nearest stop
    if waypoints:
        # Create a polyline for the route
        folium.PolyLine(locations=waypoints, color='orange', weight=5, opacity=0.7).add_to(m)

    # Save the map to an HTML file
    m.save('bus_route_map.html')
    print("Map saved as bus_route_map.html")

user_location_data = {'lat': 31.325444, 'lng': -89.348104}

nearest_stop, next_arrival, following_arrival = calculate_bus_eta(
    user_location_data, current_location, blue_route_converted_stops
)

# Output the result
if nearest_stop and next_arrival and following_arrival:
    print({
        "nearest_stop to bus ": nearest_stop,
        "next_arrival": next_arrival,
        "following_arrival": following_arrival
    })
else:
    print({"error": "Unable to calculate ETA"})


user_location_data = {'lat': 31.325444, 'lng': -89.348104}  # Example user location
visualize_route(user_location_data, current_location, blue_route_converted_stops)
