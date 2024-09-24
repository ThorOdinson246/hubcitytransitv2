# Collection of waypoints for the blue route of the bus in order so, that calculation of ETA will be done with waypoints in mind.
# If a user is at a location, the nearest bus stop will be found and the ETA will be calculated with the bus stop as the starting point.
# But if the buss passes the user, It will calculate ETa with consideration that bus cannot go back to the user location but have to complete and entre route and then come back to the user location.


# Get waypoints from the blue route
# Waypoints are the coordinates of the bus stops on the route

import requests

# Your Google Maps API key
API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'


def get_bus_route_waypoints():
    # Google Maps Directions API URL
    url = "https://maps.googleapis.com/maps/api/directions/json"

    # Parameters for the API request
    params = {
        # Starting point of the bus route
        'origin': '31.324905, -89.331087' , # Starting point of the bus route
        'destination': '31.324413, -89.374324',  # Ending point of the bus route  # Ending point of the bus route
        'mode': 'transit',  # Mode of travel: transit (bus)
        'key': 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ',

        # 'transit_mode': 'bus',  # Transit mode: bus
    }

    # Make the API request to Google Directions API
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        waypoints = []
        steps = data['routes'][0]['legs'][0]['steps']

        # Extract waypoints (bus stops) from the steps
        for step in steps:
            if 'transit_details' in step:
                # Transit details include bus stop locations
                waypoints.append({
                    'stop_name': step['transit_details']['departure_stop']['name'],
                    'location': {
                        'lat': step['transit_details']['departure_stop']['location']['lat'],
                        'lng': step['transit_details']['departure_stop']['location']['lng']
                    }
                })
                waypoints.append({
                    'stop_name': step['transit_details']['arrival_stop']['name'],
                    'location': {
                        'lat': step['transit_details']['arrival_stop']['location']['lat'],
                        'lng': step['transit_details']['arrival_stop']['location']['lng']
                    }
                })
                print("waypoint added")

        return waypoints
    else:
        print(f"Error fetching directions: {data['status']}")
        return None


# Example usage
origin = "Starting Bus Stop Address"
destination = "Ending Bus Stop Address"
waypoints = get_bus_route_waypoints()

# Print out the waypoints (bus stops along the route)
if waypoints:
    for waypoint in waypoints:
        print(
            f"Bus Stop: {waypoint['stop_name']}, Location: {waypoint['location']}")
        
else:
    print("No waypoints found")
