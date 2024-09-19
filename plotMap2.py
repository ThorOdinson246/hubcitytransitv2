import folium
from pyproj import Transformer
from getDataFromArcGIS import getDataFromArcGIS
from routes import paths_blueroute, paths_goldrouteusm, paths_greenroute
# Initialize the transformer to convert from EPSG:3857 to EPSG:4326
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")

# instance of getDataFromArcGIS
data_source=getDataFromArcGIS("https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1")
# Convert the coordinates from EPSG:3857 to EPSG:4326
def convert_coordinates(paths):
    converted_paths = [
        [transformer.transform(x, y)[0], transformer.transform(x, y)[1]] for x, y in paths
    ]
    return converted_paths


# Hattiesburg coordinates
m = folium.Map(location=[31.3271, -89.2903], zoom_start=13,)


folium.PolyLine(locations=convert_coordinates(paths_blueroute), color='#3a72ff',).add_to(m)
folium.PolyLine(locations=convert_coordinates(paths_goldrouteusm), color='#ffcc00').add_to(m)
folium.PolyLine(locations=convert_coordinates(paths_greenroute), color='#53a600').add_to(m)

folium.Marker(location=data_source.get_last_known_location([9]), popup='Blue2').add_to(m)
# Save the map to an HTML file
m.save('index.html')

