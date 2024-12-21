import json
from pyproj import Transformer
# Convert the coordinates from EPSG:3857 to EPSG:4326
def convert_coordinates(x, y):
    transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
    return transformer.transform(x, y)

def extract_bus_stops(input_file, output_file):
    try:
        # Open the input JSON file
        with open(input_file, 'r') as f:
            data = json.load(f)

        bus_stops = []
        # Navigate through the nested structure in the JSON
        for operational_layer in data.get('operationalLayers', []):
            feature_collection = operational_layer.get('featureCollection', {})
            for layer in feature_collection.get('layers', []):
                for feature in layer.get('featureSet', {}).get('features', []):
                    attributes = feature.get('attributes', {})
                    geometry = feature.get('geometry', {})
                    # Check if the Route is "Gold Line (USM)"
                    if attributes.get('Route', '') == 'Gold Line (USM)':
                        # Convert coordinates and create a bus stop dictionary
                        bus_stop = {
                            'x': convert_coordinates(0, geometry.get('y'))[0],#
                            'y': convert_coordinates(geometry.get('x'), 0)[1],
                            'location': attributes.get('Location', 'Unknown'),
                            'direction': attributes.get('Direction', 'Unknown'),
                        }
                        # Add the bus stop to the list
                        bus_stops.append(bus_stop)
        
        # Write the bus stops data to the output JSON file
        with open(output_file, 'w') as f:
            json.dump(bus_stops, f, indent=2)
        print(f"Bus stops data saved to {output_file}")
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {input_file} is not a valid JSON file.")
    except KeyError as e:
        print(f"Error: {e}")


# TO check the function 
if __name__ == "__main__":
    input_file = 'data_from_webmap_json.json'
    extract_bus_stops(input_file, 'gold_route_stops.json')


