import os
import numpy as np
from PIL import Image

# Input image path
image_path = "highResMeta/SiteC.png"

# Output directory
output_dir = "crop"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Load the image
img = Image.open(image_path)
width, height = img.size

# Define the crop size
crop_size = 256

# Calculate number of crops in each dimension
num_crops_w = width // crop_size
num_crops_h = height // crop_size

# Crop and save images
for i in range(num_crops_h):
    for j in range(num_crops_w):
        # Calculate coordinates for cropping
        left = j * crop_size
        top = i * crop_size
        right = left + crop_size
        bottom = top + crop_size
        
        # Crop the image
        cropped = img.crop((left, top, right, bottom))
        
        # Save as .tif
        output_path = os.path.join(output_dir, f"crop_{i}_{j}.png")
        cropped.save(output_path, format='png')

print(f"Finished cropping! Created {num_crops_w * num_crops_h} images of size {crop_size}x{crop_size}")
