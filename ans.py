#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 21:14:45 2019

@author: tudou
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 16:21:00 2019

@author: tudou
"""
import pandas as pd
import numpy as np
import time
from pyeasyga import pyeasyga
def create_individual(data):
    data=plane_data_in
    x=np.zeros((4, 11))
    ran=np.array([0 for _ in range(0,11)])    
    for i in range(0,11):
        s=0
        l=[]
        for j in range(0,i):
            if data[j,1]>data[i,0]:
                s+=1
                l.append(ran[j])
        temp=random.randint(0,3-s)
        l.sort()
        for k in l:
            if k<=temp:
                temp+=1
        ran[i]=temp
        x[temp,i]=1
    x=x.astype(int).flatten().tolist()
    return x
def fitness(individual, data):
    values=0
    x=individual
    x=np.array(x)
    x.shape=(4,11)
    for i in range(0,11):
        for j in range(0,4):
            if x[j,i]:
                values+=np.sum(data[i,2:5]*G_data_in[j,:])
    def check(xx):
        for ii in range(0,11):
            if np.sum(xx[:,ii])!=1:
                return False
        ran=np.array([0 for _ in range(0,11)])
        for i in range(0,11):
            for j in range(0,4):
                if xx[j,i]==1:
                    ran[i]=j
        for i in range(0,11):
            for j in range(0,i):
                if data[j,1]>data[i,0] and ran[i]==ran[j]:
                    return False  
        return True
    if not check(x):
        values=np.inf
    return values
t_in=time.time()
plane_data_in=np.array(pd.read_csv('./plane.csv',header=None))
G_data_in=np.array(pd.read_csv('./G.csv',header=None))
plane_4=np.r_[plane_data_in,plane_data_in,plane_data_in,plane_data_in]
#ga = pyeasyga.GeneticAlgorithm(plane_4,population_size=200,
#                               generations=200,maximise_fitness=False)#,elitism=True
#
ga = pyeasyga.GeneticAlgorithm(data,
                               population_size=50,
                               generations=50,
                               crossover_probability=0.8,
                               mutation_probability=0.1,
                               elitism=True,
                               maximise_fitness=False)


ga.fitness_function = fitness               # set the GA's fitness function
ga.create_individual=create_individual
ga.run()                                    # run the GA
print(ga.best_individual())                  # print the GA's best solution
t=np.array(ga.best_individual()[1])

t.shape=(4,11)
print(t)
s=0
for i in range(0,11):
    for j in range(0,4):
        if t[j,i]:
            s+=np.sum(plane_4[i,2:5]*G_data_in[j,:])

print(s)

ran=np.array([0 for _ in range(0,11)])
for i in range(0,11):
    for j in range(0,4):
        if t[j,i]==1:
            ran[i]=j+1

print("停机位:",ran)
t_fin=time.time()
print("耗时:",t_fin-t_in,"s")