import folium
from pyproj import Transformer
from getDataFromArcGIS import getDataFromArcGIS
from getCurrentLocation import DeviceLocationFetcher
from routes import paths_blueroute, paths_goldrouteusm, paths_greenroute
# Initialize the transformer to convert from EPSG:3857 to EPSG:4326
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")

# instance of getDataFromArcGIS
# Convert the coordinates from EPSG:3857 to EPSG:4326
def convert_coordinates(paths):
    converted_paths = [
        [transformer.transform(x, y)[0], transformer.transform(x, y)[1]] for x, y in paths
    ]
    return converted_paths

# COMMENT C@ HERE
# get the current location of the device
feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
device_id = "E258CD5E-7937-450B-9684-0318A2523DAD"
fetcher = DeviceLocationFetcher(feature_layer_url)
location = fetcher.get_device_location(device_id)
print(location)
# UNCOMMENT C@ HERE


# Hattiesburg coordinates
m = folium.Map(location=[31.3271, -89.2903], zoom_start=13,)


folium.PolyLine(locations=convert_coordinates(paths_blueroute), color='#3a72ff',).add_to(m)
# folium.PolyLine(locations=convert_coordinates(paths_goldrouteusm), color='#ffcc00').add_to(m)
# folium.PolyLine(locations=convert_coordinates(paths_greenroute), color='#53a600').add_to(m)
folium.Marker(location=location, popup='Blue').add_to(m)


# folium.Marker(location=, popup='Blue2').add_to(m)
# Save the map to an HTML file
m.save('index.html')

