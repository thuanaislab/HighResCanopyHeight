import os
import numpy as np
from osgeo import gdal, osr
import xml.etree.ElementTree as ET
import re

def extract_coordinates_from_kml(kml_path):
    # Parse KML file
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    # Find coordinates in KML (assuming they're in a <coordinates> tag)
    # Remove namespace for easier parsing
    ns = re.match(r'{.*}', root.tag).group(0)
    coord_elem = root.find(f".//{ns}coordinates")
    
    if coord_elem is None:
        raise ValueError("No coordinates found in KML file")
        
    # Parse coordinate string
    coord_str = coord_elem.text.strip()
    coords = []
    for point in coord_str.split():
        lon, lat, _ = map(float, point.split(','))
        coords.append((lon, lat))
    
    return coords

def create_geotiff(chm_array, kml_path, output_path):
    # Load coordinates from KML
    coords = extract_coordinates_from_kml(kml_path)
    
    # Get bounds
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    
    # Get array dimensions
    height, width = chm_array.shape
    
    # Calculate pixel size
    pixel_width = (max_lon - min_lon) / width
    pixel_height = (max_lat - min_lat) / height
    
    # Create geotransform
    # (top_left_x, pixel_width, 0, top_left_y, 0, -pixel_height)
    geotransform = (min_lon, pixel_width, 0, max_lat, 0, -pixel_height)
    
    # Create the GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    dataset = driver.Create(output_path, width, height, 1, gdal.GDT_Float32)
    
    # Set geotransform and projection
    dataset.SetGeoTransform(geotransform)
    
    # Set projection to WGS84
    srs = osr.SpatialReference()
    srs.SetWellKnownGeogCS('WGS84')
    dataset.SetProjection(srs.ExportToWkt())
    
    # Write the data
    band = dataset.GetRasterBand(1)
    band.WriteArray(chm_array)
    band.SetNoDataValue(-9999)
    
    # Close the dataset
    dataset = None

# Load the merged CHM
merged_chm = np.load("merged_CHM.npy")

# Create georeferenced TIFF
kml_path = "highResMeta/kml.kml"
output_tiff = "merged_CHM_satellite.tif"

create_geotiff(merged_chm, kml_path, output_tiff)
print(f"Created georeferenced TIFF file: {output_tiff}") 