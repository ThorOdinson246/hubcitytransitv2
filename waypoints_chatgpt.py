import requests

# Your Google Maps API key
API_KEY = 'AIzaSyBoID4hGG76qKDakJTT_eywoGSF1CIL3iQ'

def get_transit_stops(origin, destination):
    # Directions API URL
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    # Parameters for the API request
    params = {
        'origin': origin,  # Starting point of the route
        'destination': destination,  # Ending point of the route
        'mode': 'transit',  # Transit mode to get bus route
        'transit_mode': 'bus',  # Specify bus
        'key': API_KEY
    }

    # Make the request to the Directions API
    response = requests.get(url, params=params)
    data = response.json()

    if data['status'] == 'OK':
        stops = []
        steps = data['routes'][0]['legs'][0]['steps']

        # Extract the transit details (bus stops) from the steps
        for step in steps:
            if 'transit_details' in step:
                # Get the departure and arrival bus stops
                departure_stop = {
                    'name': step['transit_details']['departure_stop']['name'],
                    'location': {
                        'lat': step['transit_details']['departure_stop']['location']['lat'],
                        'lng': step['transit_details']['departure_stop']['location']['lng']
                    }
                }
                arrival_stop = {
                    'name': step['transit_details']['arrival_stop']['name'],
                    'location': {
                        'lat': step['transit_details']['arrival_stop']['location']['lat'],
                        'lng': step['transit_details']['arrival_stop']['location']['lng']
                    }
                }

                # Add bus stops to the list
                stops.append(departure_stop)
                stops.append(arrival_stop)

        return stops
    else:
        print(f"Error: {data['status']}")
        return None

# Example usage
origin = "Hattiesburg Station, Hattiesburg, MS"  # Starting location along the Blue Line
destination = "The University Of Southern Mississippi, Hattiesburg, MS"  # Destination location along the Blue Line

bus_stops = get_transit_stops(origin, destination)

if bus_stops:
    for stop in bus_stops:
        print(f"Bus Stop: {stop['name']}, Location: {stop['location']}")
