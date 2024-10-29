# import folium
# from folium.plugins import Realtime
# from pyproj import Transformer
# from utils.getDataFromArcGIS import getDataFromArcGIS
# from utils.getCurrentLocation import DeviceLocationFetcher
# from utils.deviceIDs import device_id
# from misc.routes import paths_blueroute, paths_goldrouteusm, paths_greenroute
# # Initialize the transformer to convert from EPSG:3857 to EPSG:4326
# transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326")

# # instance of getDataFromArcGIS
# # Convert the coordinates from EPSG:3857 to EPSG:4326
# def convert_coordinates(paths):
#     converted_paths = [
#         [transformer.transform(x, y)[0], transformer.transform(x, y)[1]] for x, y in paths
#     ]
#     return converted_paths

# # def convert_coordinates(coordinate):

# # COMMENT C@ HERE
# # get the current location of the device
# feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
# fetcher = DeviceLocationFetcher(feature_layer_url)
# location = fetcher.get_bus_location(device_id["gold1"])
# print(location)
# # UNCOMMENT C@ HERE


# # Hattiesburg coordinates
# # Map 
# m = folium.Map(location=[31.3271, -89.2903], zoom_start=13,width="1200px" , height="1200px")


# folium.PolyLine(locations=convert_coordinates(paths_blueroute), color='#3a72ff',).add_to(m)
# folium.PolyLine(locations=convert_coordinates(paths_goldrouteusm), color='#ffcc00').add_to(m)
# folium.PolyLine(locations=convert_coordinates(paths_greenroute), color='#53a600').add_to(m)
# folium.Marker(location=[31.3271, -89.2903], popup='Hattiesburg').add_to(m)
# folium.Marker(location=location, popup='Bluej').add_to(m)

# # Buttons for the routes
# folium.LayerControl().add_to(m)


# # REALTIME EXTENSION IMPLEMENTATION
# # source = folium.JsCode("""
# #     function(responseHandler, errorHandler) {
# #         var url = 'https://api.wheretheiss.at/v1/satellites/25544';

# #         fetch(url)
# #         .then((response) => {
# #             return response.json().then((data) => {
# #                 var { id, longitude, latitude } = data;

# #                 return {
# #                     'type': 'FeatureCollection',
# #                     'features': [{
# #                         'type': 'Feature',
# #                         'geometry': {
# #                             'type': 'Point',
# #                             'coordinates': [longitude, latitude]
# #                         },
# #                         'properties': {
# #                             'id': id
# #                         }
# #                     }]
# #                 };
# #             })
# #         })
# #         .then(responseHandler)
# #         .catch(errorHandler);
# #     }
# # """)



# # rt = Realtime(source, interval=1000)
# # rt.add_to(m)
# # REALTIME EXTENSION IMPLEMENTATION 



# # folium.Marker(location=, popup='Blue2').add_to(m)
# # Save the map to an HTML file
# m.save('index.html')

