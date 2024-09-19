from arcgis.gis import GIS
from arcgis.features import FeatureLayer

class DeviceLocationFetcher:
    def __init__(self, feature_layer_url, username=None, password=None):
        
        self.gis = GIS(username=username, password=password)
        self.feature_layer = FeatureLayer(feature_layer_url)

    def get_device_location(self, device_id):
        
        query_result = self.feature_layer.query(where=f"device_id='{device_id}'", out_fields="*")
        
        if query_result.features:
            feature = query_result.features[0]
            geometry = feature.geometry
            latitude = geometry['y']
            longitude = geometry['x']
            return latitude, longitude
        else:
            return None

# Example usage
if __name__ == "__main__":
    feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
    device_id = "07EF9193-D679-4B84-9005-9FA2D2D1D3B5"
    
    fetcher = DeviceLocationFetcher(feature_layer_url)
    location = fetcher.get_device_location(device_id)
    
    if location:
        latitude, longitude = location
        print(f"Latitude: {latitude}, Longitude: {longitude}")
    else:
        print("Device not found.")