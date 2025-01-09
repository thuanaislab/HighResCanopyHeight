import os
import torch
import pandas as pd
import numpy as np
import torchvision.transforms as T
import matplotlib.pyplot as plt
import torchmetrics
from pathlib import Path
import torch.nn as nn
from tqdm import tqdm
from PIL import Image
import math
import torchvision.transforms.functional as TF
import torchvision
from torchvision.utils import save_image

from models.backbone import SSLVisionTransformer
from models.dpt_head import DPTHead
import pytorch_lightning as pl
from models.regressor import RNet
import inference

import seaborn as sns
import seaborn_image as isns
import matplotlib.pyplot as plt

torch.backends.quantized.engine = 'qnnpack'

device = 'cpu'
norm_path = 'saved_checkpoints/aerial_normalization_quantiles_predictor.ckpt'
ckpt = torch.load(norm_path, map_location='cpu')
state_dict = ckpt['state_dict']
checkpoint = 'saved_checkpoints/compressed_SSLhuge.pth'
PATH = 'highResMeta/crop'
OUTPUT_PATH = 'highResMeta/output'
if not os.path.exists(OUTPUT_PATH):
    os.makedirs(OUTPUT_PATH)

# 1- load normnet
for k in list(state_dict.keys()):
    if 'backbone.' in k:
        new_k = k.replace('backbone.','')
        state_dict[new_k] = state_dict.pop(k)
        
model_norm = inference.RNet(n_classes=6)
model_norm = model_norm.eval()
model_norm.load_state_dict(state_dict)


# 2- load SSL model
model = inference.SSLModule(ssl_path = checkpoint)
model.to(device)
model = model.eval()

# 3- image normalization for each image going through the encoder
norm = T.Normalize((0.420, 0.411, 0.296), (0.213, 0.156, 0.143))
norm = norm.to(device)
class TreeDataset(torch.utils.data.Dataset):
    def __init__(self, dataset_path, transform):
        self.dataset_path = dataset_path
        # Create a mapping from class label to a unique integer.        
        self.datapoints = os.listdir(self.dataset_path)
        self.datapoints = [x for x in self.datapoints if x[-4:] == '.png']
        self.transform = transform

    def __getitem__(self, idx):
        img_path = os.path.join(self.dataset_path, '/')
        # Convert image to RGB mode before converting to tensor
        input = Image.open(self.dataset_path + '/' + self.datapoints[idx]).convert('RGB')
        input = TF.to_tensor(input)
        name = self.datapoints[idx]
        if self.transform is not None:
            input = self.transform(input)
        return input, name

    def __len__(self):
        return len(self.datapoints)



data = TreeDataset(dataset_path = PATH, transform = None)
dataloader = torch.utils.data.DataLoader(data, batch_size=1, shuffle=False, num_workers=0)
for batch, name in tqdm(dataloader):
    batch.to(device)
    pred = model(norm(batch))
    fig, axs = plt.subplots(1, 2, figsize = (10, 5))
    sns.heatmap(pred.detach().numpy().squeeze(), ax = axs[0], cbar = False)
    img = batch.detach().numpy().squeeze()
    isns.imgplot(np.moveaxis(img, 0, -1), ax = axs[1])
    plt.savefig(OUTPUT_PATH + '/' + name[0])