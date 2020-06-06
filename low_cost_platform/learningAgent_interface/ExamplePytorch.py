import torch 
import torchvision
import torchvision.transforms as transforms

import torch.nn as nn
import torch.nn.functional as F

class TestExample(nn.Module):
	def __init__(self):
		super(Net, self).__init__()
		self.conv1 = nn.Conv2d(3,6,5)
		
