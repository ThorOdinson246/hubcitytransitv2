# # from app import current_location, blue_route_converted_stops
# # import googlemaps
# # from datetime import datetime
# # import numpy as np
# # from itertools import islice


# API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'
# import googlemaps
# from datetime import datetime
# import numpy as np
# from itertools import islice
# # from app import current_location, blue_route_converted_stops



# gmaps = googlemaps.Client(key=API_KEY)

# def chunked_iterable(iterable, size):
#     it = iter(iterable)
#     while True:
#         chunk = tuple(islice(it, size))
#         if not chunk:
#             break
#         yield chunk

# def calculate_direction_eta(start_location, end_location, stops, start_index, end_index):
#     if start_index <= end_index:
#         waypoints = stops[start_index:end_index + 1]
#     else:
#         waypoints = stops[start_index:] + stops[:end_index + 1]
#     # Extract coordinates for Google Maps API (ensure (lat, lon) order)
#     waypoint_coords = [(stop['x'], stop['y']) for stop in waypoints]

#     # Split waypoints into chunks of 25
#     waypoint_chunks = list(chunked_iterable(waypoint_coords, 25))
    
#     total_duration = 0
#     chunk_duration = 0
#     current_origin = start_location

#     for i, chunk in enumerate(waypoint_chunks):
#         # Add the destination to the last chunk
#         if i == len(waypoint_chunks) - 1:
#             chunk = list(chunk) + [end_location]
#         else:
#             chunk = list(chunk)
        
#         # Debugging: Print the chunk details
#         print(f"Chunk {i}:")
#         print(f"Origin: {current_origin}")
#         print(f"Destination: {chunk[-1]}")
#         print(f"Waypoints: {chunk[:-1]}")

#         # Calculate directions for the current chunk
#         route = gmaps.directions(
#             current_origin,
#             chunk[-1],
#             waypoints=chunk[:-1] if chunk[:-1] else None,
#             optimize_waypoints=False,
#             mode="driving",
#             traffic_model="optimistic",
#             departure_time=datetime.now()
#         )
        
#         # Sum the duration of each leg
#         if route:
#             chunk_duration = sum(leg['duration']['value'] for leg in route[0]['legs'])
#             total_duration += chunk_duration
#             print(f"Chunk {i} duration: {chunk_duration} seconds")
        
#         # Update the origin for the next chunk
#         current_origin = chunk[-1]
    


#     eta_minutes = total_duration // 60
#     return eta_minutes

# def find_nearest_stop(location, stops):
#     stops_array = np.array(stops)
#     location_array = np.array(location)
#     distances = np.sum((stops_array - location_array) ** 2, axis=1)
#     nearest_index = np.argmin(distances)
#     return tuple(stops_array[nearest_index])

# def calculate_buss_eta(user_location_data, current_location, blue_route_converted_stops):
#     print("Start of calculate_bus_eta function")
    
#     # User and bus location
#     user_location = (user_location_data['lat'], user_location_data['lng'])
#     bus_location = (current_location[0], current_location[1])

#     # Debugging: Print the user's and bus's location
#     print(f"User location: {user_location}")
#     print(f"Bus location: {bus_location}")

#     # Extract coordinates for bus stops
#     bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

#     # Debugging: Print bus stops to ensure they're correct
#     # print(f"Bus stops: {bus_stops}")

#     # Nearest stop to user and its index
#     nearest_stop_to_user = find_nearest_stop(user_location, bus_stops)
#     nearest_stop_index = bus_stops.index(nearest_stop_to_user)

#     # Nearest stop to bus and its index
#     nearest_stop_to_bus = find_nearest_stop(bus_location, bus_stops)
#     bus_index = bus_stops.index(nearest_stop_to_bus)

#     # Debugging: Print nearest stop to user and bus, along with indices
#     print(f"Nearest stop to user: {nearest_stop_to_user}, Index: {nearest_stop_index}, Name: {blue_route_converted_stops[nearest_stop_index]['location']}")
#     print(f"Nearest stop to bus: {nearest_stop_to_bus}, Index: {bus_index}, Name: {blue_route_converted_stops[bus_index]['location']}")

#     print("Calculating forward ETA...")

#     # Forward ETA: Bus approaching the stop
#     forward_eta = calculate_direction_eta(
#         bus_location, nearest_stop_to_user, blue_route_converted_stops, bus_index, nearest_stop_index)

#     # Debugging: Check the value of forward ETA
#     print(f"Forward ETA (approaching the stop): {forward_eta}")

#     print("Calculating reverse ETA...")

#     # Reverse ETA: Bus has passed the stop, needs to complete the entire route
#     reverse_eta = calculate_direction_eta(
#         bus_location, nearest_stop_to_user, blue_route_converted_stops[::-1], len(bus_stops) - 1 - bus_index, len(bus_stops) - 1 - nearest_stop_index)

#     # Debugging: Check the value of reverse ETA
#     print(f"Reverse ETA (looping around the route): {reverse_eta}")

#     # Checking if both ETAs are calculated properly
#     if forward_eta is not None and reverse_eta is not None:
#         print("Forward and Reverse ETA calculated successfully.")
#         next_arrival = min(forward_eta, reverse_eta)
#         following_arrival = max(forward_eta, reverse_eta)

#         nearest_stop_info = blue_route_converted_stops[nearest_stop_index]['location']
#         print(f"Next arrival: {next_arrival}, Following arrival: {following_arrival}")
#         return nearest_stop_info, next_arrival, following_arrival
#     else:
#         print("Error: Unable to calculate ETA (forward or reverse returned None)")
#         return None, None, None


# def calculate_bus_eta(user_location_data, current_location, blue_route_converted_stops):
#     print("Start of calculate_bus_eta function")
    
#     # User and bus location
#     user_location = (user_location_data['lat'], user_location_data['lng'])
#     bus_location = (current_location[0], current_location[1])

#     print(f"User location: {user_location}")
#     print(f"Bus location: {bus_location}")

#     # Extract coordinates for bus stops
#     bus_stops = [(stop['x'], stop['y']) for stop in blue_route_converted_stops]

#     # Nearest stop to user and its index
#     nearest_stop_to_user = find_nearest_stop(user_location, bus_stops)
#     nearest_stop_index = bus_stops.index(nearest_stop_to_user)

#     # Nearest stop to bus and its index
#     nearest_stop_to_bus = find_nearest_stop(bus_location, bus_stops)
#     bus_index = bus_stops.index(nearest_stop_to_bus)

#     print(f"Nearest stop to user: {nearest_stop_to_user}, Index: {nearest_stop_index}, Name: {blue_route_converted_stops[nearest_stop_index]['location']}")
#     print(f"Nearest stop to bus: {nearest_stop_to_bus}, Index: {bus_index}, Name: {blue_route_converted_stops[bus_index]['location']}")

#     print("Calculating forward ETA...")

#     try:
#         # Forward ETA: Bus approaching the stop
#         forward_eta = calculate_direction_eta(
#             bus_location, nearest_stop_to_user, blue_route_converted_stops, bus_index, nearest_stop_index)
#         print(f"Forward ETA (approaching the stop): {forward_eta}")
#     except Exception as e:
#         print(f"Error calculating forward ETA: {str(e)}")
#         forward_eta = None

#     print("Calculating reverse ETA...")

#     try:
#         # Reverse ETA: Bus has passed the stop, needs to complete the entire route
#         total_stops = len(blue_route_converted_stops)
#         if bus_index > nearest_stop_index:
#             # Bus has passed the user's stop
#             first_part = calculate_direction_eta(
#                 bus_location, 
#                 (blue_route_converted_stops[-1]['x'], blue_route_converted_stops[-1]['y']), 
#                 blue_route_converted_stops, 
#                 bus_index, 
#                 total_stops - 1
#             )
#             second_part = calculate_direction_eta(
#                 (blue_route_converted_stops[0]['x'], blue_route_converted_stops[0]['y']),
#                 nearest_stop_to_user,
#                 blue_route_converted_stops,
#                 0, 
#                 nearest_stop_index
#             )
#         else:
#             # Standard reverse calculation
#             first_part = calculate_direction_eta(
#                 bus_location, 
#                 (blue_route_converted_stops[-1]['x'], blue_route_converted_stops[-1]['y']), 
#                 blue_route_converted_stops, 
#                 bus_index, 
#                 total_stops - 1
#             )
#             second_part = calculate_direction_eta(
#                 (blue_route_converted_stops[0]['x'], blue_route_converted_stops[0]['y']),
#                 nearest_stop_to_user,
#                 blue_route_converted_stops,
#                 0, 
#                 nearest_stop_index
#             )
        
#         print(f"First part of reverse ETA: {first_part}")
#         print(f"Second part of reverse ETA: {second_part}")
        
#         reverse_eta = first_part + second_part
#         print(f"Reverse ETA (looping around the route): {reverse_eta}")
#     except Exception as e:
#         print(f"Error calculating reverse ETA: {str(e)}")
#         reverse_eta = None

#     if forward_eta is not None and reverse_eta is not None:
#         print("Forward and Reverse ETA calculated successfully.")
#         next_arrival = min(forward_eta, reverse_eta)
#         following_arrival = max(forward_eta, reverse_eta)

#         nearest_stop_info = blue_route_converted_stops[nearest_stop_index]['location']
#         print(f"Next arrival: {next_arrival}, Following arrival: {following_arrival}")
#         return nearest_stop_info, next_arrival, following_arrival
#     else:
#         print("Error: Unable to calculate ETA (forward or reverse returned None)")
#         return None, None, None
# # Example usage
# user_location_data = {'lat':31.324751, 'lng': -89.310127 }#Near hattiesburg zoo should be around 7 mins. outbound.

# # nearest_stop, next_arrival, following_arrival = calculate_bus_eta(
# #     user_location_data, current_location, blue_route_converted_stops
# # )

# # # Output the result
# # if nearest_stop and next_arrival and following_arrival:
# #     print({
# #         "nearest_stop to bus ": nearest_stop,
# #         "next_arrival": next_arrival,
# #         "following_arrival": following_arrival
# #     })
# # else:
# #     print({"error": "Unable to calculate ETA"})

