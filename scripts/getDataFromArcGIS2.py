import json
from pyproj import Transformer

def convert_coordinates(input_file, output_file):
    # Initialize the transformer for Web Mercator to WGS84
    transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    for feature in data:
        if 'x' in feature and 'y' in feature:
            x, y = feature['x'], feature['y']
            lon, lat = transformer.transform(x, y)
            feature['x'], feature['y'] = lat, lon
    
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"Converted coordinates saved to {output_file}")

if __name__ == "__main__":
    input_file = 'extracted_stops_copy.json'
    output_file = 'converted_stops.json'
    convert_coordinates(input_file, output_file)