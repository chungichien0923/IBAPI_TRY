import numpy as np
import random
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim

from torch.utils.data import random_split
from torch.utils.data import DataLoader

def set_seed(random_seed=323014):
    # 隨機種子
    # Python random module
    random.seed(random_seed)
    # Numpy
    np.random.seed(random_seed)
    # Torch
    torch.manual_seed(random_seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(random_seed)
        torch.cuda.manual_seed_all(random_seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
def setup_dataloader(hparams, train_valid_set, test_set):
    train_valid_num = len(train_valid_set)
    train_num = int((1 - hparams['valid_ratio']) * train_valid_num)
    valid_num = train_valid_num - train_num

    train_set, valid_set = random_split(train_valid_set, [train_num, valid_num])

    train_dataloader = DataLoader(train_set, batch_size=hparams['batch_size'])
    valid_dataloader = DataLoader(valid_set, batch_size=hparams['batch_size'])
    train_valid_dataloader = DataLoader(train_valid_set)
    test_dataloader = DataLoader(test_set)
    
    return train_dataloader, valid_dataloader, train_valid_dataloader, test_dataloader

def Train(hparams, model_structure, train_dataloader):
    model = model_structure(hparams['input_size'], hparams['hidden_size'])
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), hparams['lr'])
    
    for epoch in tqdm(range(hparams['num_epochs'])):
        # training
        train_correct = 0
        len_train = 0
        
        model.train()
        for X, y in train_dataloader:
            len_train += len(X)
            # X, y = X.to(device), y.to(device)
            optimizer.zero_grad()
            ypred = model(X)
            # print('ypred: ', ypred, '\n', 'y: ', y)
            loss = criterion(ypred, y)
            _, train_pred = torch.max(ypred, 1)
            # print('ypred: ', ypred, '\n', 'train_pred: ', train_pred)
            loss.backward()
            optimizer.step()
            
            train_correct += (train_pred.cpu() == y.cpu()).sum().item()
        
        train_acc = train_correct / len_train
        
    return model, train_acc

def Evaluate(model, valid_dataloader):
    valid_correct = 0
    len_valid = 0
    
    model.eval()
    for X, y in  valid_dataloader:
        len_valid += len(X)
        # X, y = X.to(device), y.to(device)
        with torch.no_grad():
            ypred = model(X)
            _, valid_pred = torch.max(ypred, 1)
        
            valid_correct += (valid_pred.cpu() == y.cpu()).sum().item()
    valid_acc = valid_correct / len_valid
    
    return valid_acc
    
def Optim_hidden_size(hidden_size_list, hparams, model_structure, train_dataloader, valid_dataloader):
    best_hparams = {}
    best_valid_acc = 0
    for hidden_size in hidden_size_list:
        hparams['hidden_size'] = hidden_size
        print('hparams:', hparams)
        
        # training
        model, train_acc = Train(hparams, model_structure, train_dataloader)
        print('train_acc:', train_acc)
        
        # evaluating
        valid_acc = Evaluate(model, valid_dataloader)
        print('valid_acc:', valid_acc)
        
        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            best_hparams = hparams.copy()
            
    return best_hparams, best_valid_acc

def Test(hidden_size_list, hparams, model_structure, train_dataloader, valid_dataloader, train_valid_dataloader, test_dataloader):
    """
    找出在 valid set 上最好的參數，重新用 train_valid set 的資料訓練一次。
    
    回傳值為：在 valid set 上最好的參數, 在 test set 上的準確度, 在 train_valid set 上的準確度, 超參數尋找過程中在 valid set 上最高的準確度
    """
    # get the best hyperparameter
    best_hparams, best_valid_acc = Optim_hidden_size(hidden_size_list, hparams, model_structure, train_dataloader, valid_dataloader)
    # train on the best hyperparameters and the train_valid_set
    best_model, best_model_train_acc = Train(best_hparams, model_structure, train_valid_dataloader)
    # evaluating the best model on the test_set
    best_model_valid_acc = Evaluate(best_model, test_dataloader)
    
    return best_hparams, best_model_valid_acc, best_model_train_acc, best_valid_acc