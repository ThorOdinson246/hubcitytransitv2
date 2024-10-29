from arcgis.gis import GIS
from arcgis.features import FeatureLayer
import requests
from utils.deviceIDs import device_id

class DeviceLocationFetcher:
    def __init__(self, feature_layer_url, username=None, password=None):
        
        self.gis = GIS(username=username, password=password)
        self.feature_layer = FeatureLayer(feature_layer_url)

    def get_bus_location(self, device_id):
        
        query_result = self.feature_layer.query(where=f"device_id='{device_id}'", out_fields="*")
        
        if query_result.features:
            feature = query_result.features[0]
            geometry = feature.geometry
            latitude = geometry['y']
            longitude = geometry['x']
            return latitude, longitude
        else:
            return None
        
GOOGLE_MAPS_API_KEY = "AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ"

def find_nearest_transit_stop(user_lat, user_lng):
    places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    places_params = {
        'location': f'{user_lat},{user_lng}',
        'radius': 150,  # Search within 1 km radius
        'keyword': 'bus stop',
        # 'type': 'bank',
        'key': GOOGLE_MAPS_API_KEY
    }
    new_url='https://maps.googleapis.com/maps/api/place/nearbysearch/json?keyword=bus%20stop&location=31.325075%2C-89.339472&type=transit_station&radius=150&key=AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'

    try:
        response = requests.get(places_url, params=places_params)
        response = requests.get(new_url, params=None)
        response.raise_for_status()
        places_data = response.json()

        if places_data['status'] == 'OK' and places_data['results']:
            nearest_stop = places_data['results'][0]
            stop_location = nearest_stop['geometry']['location']
            stop_name = nearest_stop['name']
            print(f"Nearest transit stop: {stop_name} at ({stop_location['lat']}, {stop_location['lng']})")
            return stop_location['lat'], stop_location['lng']
        else:
            print(f"No transit stops found near the user location: {places_data['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Places request failed: {e}")
        return None, None

def get_user_eta(user_lat, user_lng, bus_lat, bus_lng):
    nearest_stop_lat, nearest_stop_lng = find_nearest_transit_stop(user_lat, user_lng)
    if nearest_stop_lat is None or nearest_stop_lng is None:
        return None, None

    directions_url = "https://maps.googleapis.com/maps/api/directions/json"
    directions_params = {
        'origin': f'{nearest_stop_lat},{nearest_stop_lng}',
        'destination': f'{bus_lat},{bus_lng}',
        'key': GOOGLE_MAPS_API_KEY,
        'mode': 'driving',
        'transit_mode': 'bus',
        'departure_time': 'now',
        'traffic_model': 'optimistic'
    }

    try:
        response = requests.get(directions_url, params=directions_params)
        response.raise_for_status()
        directions_data = response.json()

        if directions_data['status'] == 'OK':
            leg = directions_data['routes'][0]['legs'][0]
            distance = leg['distance']['text']
            duration = leg['duration']['text']
            print(f"Route from nearest stop to bus location: {leg['start_address']} to {leg['end_address']}")
            print(f"Distance: {distance}, ETA: {duration}")
            return distance, duration
        else:
            print(f"Error in directions response: {directions_data['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Directions request failed: {e}")
        return None, None


# Example usage
if __name__ == "__main__":

    feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
    fetcher = DeviceLocationFetcher(feature_layer_url)
    
    user_lat = 31.325075, 
    user_lng = -89.339472
    bus_lat = fetcher.get_bus_location(device_id["blue1"])[0]
    bus_lng = fetcher.get_bus_location(device_id["blue1"])[1]

    distance, duration = get_user_eta(user_lat, user_lng, bus_lat, bus_lng)
    if distance and duration:
        print(f"Distance: {distance}, ETA: {duration}")
    else:
        print("Failed to get ETA")



























































































































################################################################################        
# OLD IMPLEMENTATOIN WITHOUT ROUTE DETAILS IN MIND, JUST REGUKLAR DRIVING ETA
# GOOGLE_MAPS_API_KEY = "AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ"#MY GOOGLE MAPS API KEY

# def get_user_eta(user_lat, user_lng, dest_lat, dest_lng):
    
#     url = f"https://maps.googleapis.com/maps/api/distancematrix/json?"

#     params =  {
#         'origins': f'{user_lat},{user_lng}',
#         'destinations': f'{dest_lat},{dest_lng}',
#         'key': GOOGLE_MAPS_API_KEY,

#         'mode': 'driving',  # Change to walking, bicycling, or transit if needed
#         'departure_time': 'now',  # 'now' for real-time traffic data
#         'traffic_model': 'optimistic'  # Change to pessimistic or optimistic if needed,
#     }

#     response = requests.get(url, params=params)
#     data = response.json()

#     if data['status'] == 'OK':
#         element = data['rows'][0]['elements'][0]
#         distance = element['distance']['text']
#         duration = element.get('duration_in_traffic', element['duration'])['text'] 
#         print("Successful in getting eta") # Use traffic data if available
#         return distance, duration
#     else:
#         return None, None
# OLD IMPLEMENTATOIN WITHOUT ROUTE DETAILS IN MIND, JUST REGUKLAR DRIVING ETA
#############################################################

        
    