from pyproj import Transformer
class getDataFromArcGIS:
    def __init__(self, feature_layer_url):
        from arcgis.gis import GIS
        from arcgis.features import FeatureLayer

        self.gis = GIS()
        self.feature_layer = FeatureLayer(feature_layer_url)

    def fetch_data(self):
        self.features = self.feature_layer.query().features

    def print_data(self):
        for feature in self.features:
            print(feature.attributes)

    def save_data_to_json(self, file_path):
        import json
        with open(file_path, 'w') as json_file:
            json.dump(
                [feature.attributes for feature in self.features], json_file, indent=2)


    # Just didn't felt like removing, doesnot give the location,  found out later it returns the course, which has no usecase for my project 
    # Get location is actually implemented in getCurrentLocation.py
    def get_last_known_location(self,object_id):
        last_known_location = []
        for feature in self.features:
            if feature.attributes.get("objectid") in object_id:
                last_known_location.append(feature.attributes.get("course"))
        return last_known_location
    

if __name__ == "__main__":
    feature_layer_url = "https://utility.arcgis.com/usrsvcs/servers/b02066689d504f5f9428029f7268e060/rest/services/Hosted/8bd5047cc5bf4195887cc5237cf0d3e0_Track_View/FeatureServer/1"
    fetcher = getDataFromArcGIS(feature_layer_url)
    fetcher.fetch_data() 
    # print(fetcher.get_last_known_location([9]))
    # fetcher.save_data_to_json('OnlyLocation.json')
    # fetcher.save_data_to_json('ArcGISLiveData.json')

