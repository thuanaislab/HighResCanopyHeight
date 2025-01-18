from osgeo import gdal, osr
import numpy as np
from PIL import Image
from xml.etree import ElementTree as ET
import os

def parse_kml_coordinates(kml_path):
    """Parse KML file and return coordinates."""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    namespace = {"ns": "http://www.opengis.net/kml/2.2"}
    
    coordinates = root.find(".//ns:coordinates", namespace)
    if coordinates is None:
        raise ValueError("Coordinates not found in the KML file.")
        
    coord_text = coordinates.text.strip()
    coord_pairs = coord_text.split()
    
    # Extract longitude and latitude values
    lons, lats = zip(*[(float(coord.split(",")[0]), float(coord.split(",")[1])) 
                       for coord in coord_pairs])
    return lons, lats

def create_geotiff(image_path, kml_path, output_path):
    """
    Create a georeferenced TIFF from the input image using KML coordinates.
    
    Args:
        image_path: Path to the input image
        kml_path: Path to the KML file containing coordinates
        output_path: Path where the GeoTIFF will be saved
    """
    # Read the image
    img = Image.open(image_path)
    img_array = np.array(img)
    
    # Get image dimensions
    height, width = img_array.shape[:2]
    
    # Parse KML coordinates
    lons, lats = parse_kml_coordinates(kml_path)
    
    # Get boundary coordinates
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    # Calculate pixel size (resolution)
    x_res = (max_lon - min_lon) / width
    y_res = (max_lat - min_lat) / height
    
    # Create the geotransform
    # (top_left_x, pixel_width, x_rotation, top_left_y, y_rotation, pixel_height)
    geotransform = (min_lon, x_res, 0, max_lat, 0, -y_res)
    
    # Create the GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    bands = img_array.shape[2] if len(img_array.shape) > 2 else 1
    
    dataset = driver.Create(
        output_path,
        width,
        height,
        bands,
        gdal.GDT_Byte,
        options=['COMPRESS=LZW']
    )
    
    # Set the geotransform and projection
    dataset.SetGeoTransform(geotransform)
    
    # Set the projection to WGS84
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(4326)  # WGS84
    dataset.SetProjection(srs.ExportToWkt())
    
    # Write the data
    if bands == 1:
        dataset.GetRasterBand(1).WriteArray(img_array)
    else:
        for band in range(bands):
            dataset.GetRasterBand(band + 1).WriteArray(img_array[:, :, band])
    
    # Close the dataset
    dataset = None
    
    print(f"GeoTIFF created successfully at: {output_path}")
    print(f"Spatial extent: {min_lon}, {min_lat}, {max_lon}, {max_lat}")

def main():
    # Paths to the files
    image_path = "highResMeta/SiteC.png"
    kml_path = "highResMeta/kml.kml"
    output_path = "highResMeta/SiteC_georef.tiff"
    
    # Create GeoTIFF
    create_geotiff(image_path, kml_path, output_path)

if __name__ == "__main__":
    main() 