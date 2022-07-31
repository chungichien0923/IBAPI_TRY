import torch.nn as nn
from torch.utils.data import Dataset

class CostumDataset(Dataset):
    def __init__(self, X, y):
        self.X = X.astype('float32')
        self.y = y.astype('long')#np.expand_dims(y, 1)
        
    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return (self.X[idx], self.y[idx])

class model_structure(nn.Module):
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.InputLayer = nn.Linear(input_size, hidden_size)
        self.HiddenLayer =  nn.Sequential(nn.Linear(hidden_size, 2*hidden_size),
                                          nn.ReLU(),
                                          nn.Linear(2*hidden_size, 4*hidden_size),
                                          nn.ReLU(),
                                          nn.Linear(4*hidden_size, 2*hidden_size),
                                          nn.ReLU(),
                                          nn.Linear(2*hidden_size, hidden_size),
                                          nn.ReLU()
                                          )
        self.OutputLayer = nn.Linear(hidden_size, 3)

    def forward(self, input):
        hidden = self.InputLayer(input)
        hidden = self.HiddenLayer(hidden)
        output = self.OutputLayer(hidden)
        return output