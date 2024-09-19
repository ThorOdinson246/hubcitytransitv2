import json
import folium
from plotMap2 import Transformer

class RoutePlotter:
    def __init__(self, json_file):
        # Load the JSON data from the file
        with open(json_file) as f:
            self.data = json.load(f)
        # Initialize the transformer to convert from EPSG:3857 to EPSG:4326
        self.transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")
    
    def plot_route(self, route_name):
        # Check if the expected keys exist in the JSON data
        if 'layers' not in self.data or not self.data['layers']:
            print("Error: 'layers' key not found or empty in JSON data")
            return
        
        if 'featureSet' not in self.data['layers'][0] or 'features' not in self.data['layers'][0]['featureSet']:
            print("Error: 'featureSet' or 'features' key not found in JSON data")
            return
        
        # Create a map centered around Hattiesburg, Mississippi
        m = folium.Map(location=[31.3271, -89.2903], zoom_start=13)

        # Loop through the routes in the JSON data
        route_found = False
        for feature in self.data['layers'][0]['featureSet']['features']:
            route = feature['attributes']['Route']
            
            # Check if the current route matches the selected one
            if route.strip() == route_name.strip():
                route_found = True
                print(f"Plotting route: {route_name}")
                # Extract the path for the route
                paths = feature['geometry']['paths']
                # Add the path to the map
                # CC1 Commenting this to display all routes as multiple markers 
                # for path in paths:
                #     print(f"Adding path with {len(path)} coordinates")
                #     # Convert coordinates from EPSG:3857 to EPSG:4326
                #     converted_path = [[self.transformer.transform(coord[0], coord[1])[1], self.transformer.transform(coord[0], coord[1])[0]] for coord in path]
                #     folium.PolyLine(locations=converted_path, color='blue').add_to(m)
        # Uncomment CC1 here 
               
        if not route_found:
            print(f"Route '{route_name}' not found in the data.")
        else:
            # Add a marker with a popup to display the route name
            folium.Marker(
                location=[31.3271, -89.2903],
                popup=folium.Popup(f"<b>Current Route:</b> {route_name}", max_width=300)
            ).add_to(m)
        
        # Save the map to an HTML file
        m.save(f'{route_name}.html')
        print(f"Map saved as {route_name}.html")


    def convert_coordinates(self, coord):
        # Convert coordinates from EPSG:3857 to EPSG:4326
        return self.transformer.transform(coord[0], coord[1])
# Example usage:
if __name__ == "__main__":
    plotter = RoutePlotter('routePolylineData.json')
    plotter.plot_route("Blue Route (Hardy East)")