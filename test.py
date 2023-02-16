'''
Author:  
Date: 2023-02-16 19:54:33
LastEditors:  
LastEditTime: 2023-02-16 19:54:53
Description: file content
'''
import torch
import torch_directml
dml = torch_directml.device()
tensor1 = torch.tensor([1]).to(dml) # Note that dml is a variable, not a string!
tensor2 = torch.tensor([2]).to(dml)
dml_algebra = tensor1 + tensor2
dml_algebra.item()
print(dml_algebra.item())