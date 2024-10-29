# from utils.getCurrentLocation import DeviceLocationFetcher
# from utils.deviceIDs import device_id

# class BusPlotter:
#     def __init__(self, feature_layer_url, device_id):
#         self.fetcher = DeviceLocationFetcher(feature_layer_url)
#         self.device_id = device_id

#     def get_location(self,device_id):
#         location = self.fetcher.get_bus_location(device_id)
#         if location:
#             latitude, longitude = location
#             return [latitude, longitude]
#         else:
#             return None
