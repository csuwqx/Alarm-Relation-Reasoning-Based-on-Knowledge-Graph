import os, sys
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


from test import test
from train import train
from GRM import GRM
from args import args
from dataset import alarmDataset
from dataloader import alarmDataloader


if args.manualSeed is None:
    args.manualSeed = random.randint(1, 10000)
print("Random Seed: ", args.manualSeed)
random.seed(args.manualSeed)
torch.manual_seed(args.manualSeed)#为CPU设置随机种子

if args.cuda:
    torch.cuda.manual_seed_all(args.manualSeed)#为所有GPU设置随机种子

def main():
    print(args)

    #Create dataloader
    print('====>Create dataloader...')
    train_dataset = alarmDataset(args.alarm_data, True)
    train_dataloader = alarmDataloader(dataset=train_dataset, num_workers=args.workers,
                                  batch_size = args.batch_size, shuffle = True)

    test_dataset = alarmDataset(args.alarm_data, False)
    test_dataloader = alarmDataloader(dataset=test_dataset, num_workers=args.workers,
                                       batch_size=args.batch_size, shuffle=True)

    #Create Adjacency_matrix
    adjacency_matrix = create_adjacency_matrix(args.Graph_structure)
    #print(adjacency_matrix)


    #load network
    print('====>Loading the network...')
    model = GRM(adjacency_matrix)
    #print(model)

    # load pretrain model
    '''if args.weights:
        if os.path.isfile(args.weights):
            print("====> loading model '{}'".format(args.weights))
            checkpoint = torch.load(args.weights)
            checkpoint_dict = {k.replace('module.', ''): v for k, v in checkpoint['state_dict'].items()}
            model.load_state_dict(checkpoint_dict)
        else:
            print("====> no pretrain model at '{}'".format(args.weights))'''


    criterion = nn.CrossEntropyLoss()

    if args.cuda:
        model.cuda()
        criterion.cuda()

    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    
    for epoch in range(0,args.niter):
        train(epoch,train_dataloader, model, criterion, optimizer, args)
        test(test_dataloader, model, criterion, optimizer, args)

def create_adjacency_matrix(PATH):
    data_list = []
    k = 0
    with open(PATH, 'r') as f:
        for line in f:
            temp_list = []
            line_tokens = line.split(" ")
            #print(line_tokens)
            for i in range(0, len(line_tokens)):
               temp_list.append(int(line_tokens[i]))
            data_list.append(temp_list)
        adj_matrix = np.zeros([len(line_tokens), len(line_tokens)])
        print(adj_matrix.shape)
        for data in data_list:
            for j in range(0,len(data)):            
                adj_matrix[k][j] = data[j]
            k = k+1
        f.close()
    return adj_matrix


def find_max_node(node_list):
    max_node_id = 0
    for node in node_list:
        if node > max_node_id:
            max_node_id = node
    return max_node_id

if __name__=='__main__':
    main()
