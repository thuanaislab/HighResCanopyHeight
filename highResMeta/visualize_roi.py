from PIL import Image
from xml.etree import ElementTree as ET
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib_scalebar.scalebar import ScaleBar
import math

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

def get_boundary_coords(lons, lats):
    """Get min/max coordinates from lists of lons and lats."""
    return min(lons), max(lons), min(lats), max(lats)

def calculate_distance_meters(lon1, lat1, lon2, lat2):
    """Calculate distance between two points in meters using Haversine formula."""
    R = 6371000  # Earth's radius in meters
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c

def visualize_boundaries(image_path, reference_kml, roi_kml, output_path="tmp/roi_visualization.png"):
    """
    Visualize the ROI boundary on the image with a scale bar.
    
    Args:
        image_path: Path to the image
        reference_kml: Path to the reference KML file (used for GPS alignment)
        roi_kml: Path to the ROI KML file to be visualized
        output_path: Path where the output image will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Parse both KML files
    ref_lons, ref_lats = parse_kml_coordinates(reference_kml)
    roi_lons, roi_lats = parse_kml_coordinates(roi_kml)
    
    # Get reference boundary coordinates for GPS alignment
    min_lon, max_lon, min_lat, max_lat = get_boundary_coords(ref_lons, ref_lats)
    
    # Calculate image scale (meters per pixel)
    img_width_meters = calculate_distance_meters(min_lon, (min_lat + max_lat)/2,
                                               max_lon, (min_lat + max_lat)/2)
    
    # Read the image
    img = plt.imread(image_path)
    img_height, img_width = img.shape[:2]
    
    # Calculate meters per pixel
    meters_per_pixel = img_width_meters / img_width
    
    # Create figure and axis
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(img)
    
    # Convert ROI coordinates to pixel coordinates
    roi_x_pixels = [(lon - min_lon) / (max_lon - min_lon) * img_width for lon in roi_lons]
    roi_y_pixels = [(lat - min_lat) / (max_lat - min_lat) * img_height for lat in roi_lats]
    roi_y_pixels = [img_height - y for y in roi_y_pixels]  # Invert y-axis
    
    # Plot ROI boundary with dashed line
    ax.plot(roi_x_pixels, roi_y_pixels, 'r--', linewidth=2, label='ROI Boundary')
    
    # Add single 500m scale bar
    scalebar = ScaleBar(
        meters_per_pixel,
        location='lower left',
        box_alpha=0.5,
        fixed_value=500,
        fixed_units='m',
        scale_loc='top',
        length_fraction=0.25,
        height_fraction=0.02,
        pad=0.15
    )
    ax.add_artist(scalebar)
    
    # Calculate center coordinates
    center_lon = (min_lon + max_lon) / 2
    center_lat = (min_lat + max_lat) / 2
    
    # Add center coordinates text
    plt.text(
        img_width/2, img_height/2,
        f"{abs(center_lon):.3f}°W, {center_lat:.3f}°N",
        color='black',
        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=3),
        ha='center',
        va='center',
        fontsize=10
    )
    
    plt.legend()
    plt.axis('off')
    
    # Crop the figure after plotting everything
    crop_fraction = 0.8
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    
    # Calculate new limits
    x_center = (xlim[1] + xlim[0]) / 2
    y_center = (ylim[1] + ylim[0]) / 2
    x_range = xlim[1] - xlim[0]
    y_range = ylim[1] - ylim[0]
    
    # Set new limits
    ax.set_xlim(x_center - x_range * crop_fraction / 2,
                x_center + x_range * crop_fraction / 2)
    ax.set_ylim(y_center - y_range * crop_fraction / 2,
                y_center + y_range * crop_fraction / 2)
    
    # Save the plot
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()

if __name__ == "__main__":
    # Paths to the files
    image_path = "highResMeta/SiteC.png"
    reference_kml = "highResMeta/kml.kml"
    roi_kml = "highResMeta/ROI.kml"
    
    # Visualize boundaries
    visualize_boundaries(image_path, reference_kml, roi_kml, 
                         output_path="tmp/roi_visualization.pdf")
    print("Visualization saved to tmp/roi_visualization.png") 