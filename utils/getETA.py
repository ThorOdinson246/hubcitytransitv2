# import googlemaps
# from datetime import datetime
# import numpy as np
# from app import current_location, blue_route_converted_stops

# API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'
# gmaps=googlemaps.Client(key=API_KEY)

# # Find the nearest stop to the user's location
# def find_nearest_stop(location, stops):
#     stops_array = np.array(stops)
#     location_array = np.array(location)
#     distances = np.sum((stops_array - location_array) ** 2, axis=1)
#     nearest_index = np.argmin(distances)
#     return tuple(stops_array[nearest_index])

