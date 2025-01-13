import os
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

# Original image path to get dimensions
original_img_path = "highResMeta/SiteC.png"
original_img = Image.open(original_img_path)
original_width, original_height = original_img.size

# Directory containing the CHM prediction files (.npy)
prediction_dir = "output"  # Change this to your prediction directory
crop_size = 256

# Create empty array for the merged result
merged_chm = np.zeros((original_height, original_width))

# Calculate number of crops in each dimension
num_crops_w = original_width // crop_size
num_crops_h = original_height // crop_size

# Merge predictions
for i in range(num_crops_h):
    for j in range(num_crops_w):
        # Load the prediction file
        pred_path = os.path.join(prediction_dir, f"crop_{i}_{j}.npy")
        if os.path.exists(pred_path):
            pred = np.load(pred_path)
            
            # Calculate positions
            top = i * crop_size
            left = j * crop_size
            
            # Place the prediction in the merged array
            merged_chm[top:top+crop_size, left:left+crop_size] = pred

# Save the merged result
np.save("merged_CHM.npy", merged_chm)

print(f"Merged CHM saved with shape: {merged_chm.shape}")

# Visualize the merged CHM
plt.figure(figsize=(12, 8))
plt.imshow(merged_chm, cmap='viridis')
plt.colorbar(label='Canopy Height (m)')
plt.title('Merged Canopy Height Model')
plt.axis('off')
plt.savefig('merged_CHM_visualization.png', dpi=300, bbox_inches='tight')
plt.close()

print("Visualization saved as 'merged_CHM_visualization.png'")
