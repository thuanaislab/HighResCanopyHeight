from PIL import Image
from xml.etree import ElementTree as ET
import math
import matplotlib.pyplot as plt
import numpy as np
import os

def visualize_boundary(image_path, lons, lats, min_lon, max_lon, min_lat, max_lat, output_path="tmp/bound.png"):
    """
    Visualize the KML boundary overlaid on the image.
    
    Args:
        image_path: Path to the image
        lons, lats: Lists of longitude and latitude coordinates
        min_lon, max_lon, min_lat, max_lat: Boundary coordinates
        output_path: Path where the output image will be saved
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Read the image
    img = plt.imread(image_path)
    
    # Create figure and axis
    plt.figure(figsize=(12, 8))
    plt.imshow(img)
    
    # Convert geographic coordinates to pixel coordinates
    img_height, img_width = img.shape[:2]
    x_pixels = [(lon - min_lon) / (max_lon - min_lon) * img_width for lon in lons]
    y_pixels = [(lat - min_lat) / (max_lat - min_lat) * img_height for lat in lats]
    
    # Invert y-axis since image coordinates start from top
    y_pixels = [img_height - y for y in y_pixels]
    
    # Plot the boundary
    plt.plot(x_pixels, y_pixels, 'r-', linewidth=2, label='KML Boundary')
    
    # Add markers at the corners
    plt.plot(x_pixels, y_pixels, 'bo', markersize=5)
    
    plt.title('Image with KML Boundary')
    plt.legend()
    plt.axis('off')
    
    # Save the plot
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    
if __name__ == "__main__":
    # Paths to the image and KML files
    image_path = "highResMeta/SiteC.png"
    kml_path = "highResMeta/kml.kml"

    # Step 1: Open the image to get its dimensions
    image = Image.open(image_path)
    image_width, image_height = image.size

    # Step 2: Parse the KML file to extract bounding box coordinates
    tree = ET.parse(kml_path)
    root = tree.getroot()

    # Define the namespace for KML
    namespace = {"ns": "http://www.opengis.net/kml/2.2"}

    # Find the coordinates in the KML
    coordinates = root.find(".//ns:coordinates", namespace)
    if coordinates is not None:
        coord_text = coordinates.text.strip()
        coord_pairs = coord_text.split()

        # Extract longitude and latitude values
        lons, lats = zip(*[(float(coord.split(",")[0]), float(coord.split(",")[1])) for coord in coord_pairs])
        min_lon, max_lon = min(lons), max(lons)
        min_lat, max_lat = min(lats), max(lats)

        # Step 3: Calculate GSD in degrees per pixel
        lon_range = max_lon - min_lon  # Longitude range
        lat_range = max_lat - min_lat  # Latitude range
        gsd_lon = lon_range / image_width  # Degrees per pixel in longitude
        gsd_lat = lat_range / image_height  # Degrees per pixel in latitude

        # Step 4: Convert GSD to meters per pixel
        meters_per_degree_lat = 111320  # Approx. meters per degree of latitude
        average_lat = (min_lat + max_lat) / 2  # Average latitude of the region

        # Meters per degree of longitude depends on latitude
        meters_per_degree_lon = meters_per_degree_lat * math.cos(math.radians(average_lat))

        # GSD in meters per pixel
        gsd_lon_meters = gsd_lon * meters_per_degree_lon
        gsd_lat_meters = gsd_lat * meters_per_degree_lat

        # Print results
        print("Bounding Box:")
        print(f"  Longitude: {min_lon} to {max_lon}")
        print(f"  Latitude: {min_lat} to {max_lat}")
        print("\nImage Dimensions:")
        print(f"  Width: {image_width} pixels")
        print(f"  Height: {image_height} pixels")
        print("\nGround Sample Distance (GSD):")
        print(f"  Longitude: {gsd_lon:.10f} degrees/pixel (~{gsd_lon_meters:.4f} meters/pixel)")
        print(f"  Latitude: {gsd_lat:.10f} degrees/pixel (~{gsd_lat_meters:.4f} meters/pixel)")

        # Call the visualization function
        visualize_boundary(image_path, lons, lats, min_lon, max_lon, min_lat, max_lat)
    else:
        print("Coordinates not found in the KML file.")

