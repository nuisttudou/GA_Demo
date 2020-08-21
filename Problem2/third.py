#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 22:32:23 2020

@author: tudou
"""

import pandas as pd
import numpy as np
import time
import random
import heapq

from pyeasyga import pyeasyga
t_in=time.time()

NUM_OF_PLANE=374
NUM_OF_G=199

#%%读取
info_data_in=pd.read_csv('航班信息表1.csv',header=0)
plane_park_in=pd.read_csv('./CAN登机口信息表(8.12).csv',header=0)


plane_index=np.array(info_data_in['序号']).astype(int)
plane_country=np.array(info_data_in['属性']).astype(int)#国内/国际
plane_in_time=np.array(info_data_in['计划到达']).astype(float)
plane_out_time=np.array(info_data_in['计划起飞']).astype(float)
plane_category=np.array(info_data_in['机位型']).astype(int)

plane_passengers=np.array(info_data_in['旅客人数']).astype(int)
plane_arrive_people=np.array(info_data_in['到达人数']).astype(int)
plane_exit_people=np.array(info_data_in['出发人数']).astype(int)
plane_passby_people=np.array(info_data_in['中转人数']).astype(int)
#%%

park_index=np.array(plane_park_in['近/远机位登机口']).astype(int)
park_is_near=np.array(plane_park_in['近/远机位登机口']).astype(int)
park_country=np.array(plane_park_in['国际/国内']).astype(int)
park_category=np.array(plane_park_in['登机口对应机位等级']).astype(int)
park_walk_time=np.array(plane_park_in['步行时间']).astype(float)

park_port=np.array(plane_park_in['登机口对应的机位']).astype(int)

park_arrive_walk_time=np.array(plane_park_in['到达行走时间']).astype(float)
park_exit_walk_time=np.array(plane_park_in['出发行走时间']).astype(float)
park_passby_walk_time=np.array(plane_park_in['中转行走时间']).astype(float)



#%% 映射

park_port_set=list(set(park_port))
port2num={}
num2port={}

for i in range(0,len(park_port_set)):
    num2port[i]=park_port_set[i]
    port2num[park_port_set[i]]=i
    
park_port_num=[port2num[i] for i in park_port] #登机口对应的机位

#%% 国内国际机位

can_use_country=[[],[],[]] #park
for i in range(0,NUM_OF_G):
    if can_use_country[park_country[i]].count(park_port_num[i])==0:
        can_use_country[park_country[i]].append(park_port_num[i])

for i in range(0,len(can_use_country[2])):
    if can_use_country[0].count(can_use_country[2][i])==0:
        can_use_country[0].append(can_use_country[2][i])
    if can_use_country[1].count(can_use_country[2][i])==0:
        can_use_country[1].append(can_use_country[2][i])


#%% CDEF种类
can_use_category=[[],[],[],[],[]] #park 
for i in range(0,NUM_OF_G):
    if can_use_category[park_category[i]].count(park_port_num[i])==0:
        can_use_category[park_category[i]].append(park_port_num[i])

#%%
is_remote=(plane_out_time-plane_in_time)>=6/24
plane_remote_index=[i for i in range(0,NUM_OF_PLANE) if is_remote[i]]
plane_remote_num=len(plane_remote_index)
NUM_OF_PLANE_CALCULATE=NUM_OF_PLANE-plane_remote_num

#%%
data=[]

class P:
    def __init__(self,port_num,outtime):
        self.port_num=port_num
        self.outtime=outtime
    def __lt__(self,other):
        return self.outtime<other.outtime
    
#%%
def create_individual(data):
    port_canuse_country=[set(can_use_country[0]),set(can_use_country[1])]
    port_canuse_category=[[],set(can_use_category[1]),set(can_use_category[2])
                          ,set(can_use_category[3]),set(can_use_category[4])]
    plane_have_port=[]
    used_prot_heap=[]
    for i in range(0,NUM_OF_PLANE):
        if is_remote[i]:
            continue
        now_intime=plane_in_time[i]
        while len(used_prot_heap)>0 and used_prot_heap[0].outtime<=now_intime:
            top_item=heapq.heappop(used_prot_heap)
            top=top_item.port_num
            if park_country[top]==0 or park_country[top]==2:
                port_canuse_country[0].add(top)
            if park_country[top]==1 or park_country[top]==2:
                port_canuse_country[1].add(top)    
        my_can_use=set() #当前候选机位
        for j in range(plane_category[i],5):#4为种类上限
            my_can_use=my_can_use or port_canuse_category[j]
        my_can_use=my_can_use and port_canuse_country[plane_country[i]]
        my_can_use_list=list(my_can_use)
        now_have_port_index=random.randint(0,len(my_can_use)-1)
        now_have_port=my_can_use_list[now_have_port_index]
        now_have_finished_time=plane_out_time[i]
        if now_have_port in port_canuse_country[0]:
            port_canuse_country[0].remove(now_have_port)
        if now_have_port in port_canuse_country[1]:
            port_canuse_country[1].remove(now_have_port)
        heapq.heappush(used_prot_heap,P(now_have_port,now_have_finished_time+5/60/24))# 5分钟安全
        plane_have_port.append(now_have_port)
    return plane_have_port

#%%

M1=0.36
M2=0.64
MAXX=60078*20.58


def pan(wait_check_plane):
    port_canuse_country=[set(can_use_country[0]),set(can_use_country[1])]
    port_canuse_category=[[],set(can_use_category[1]),set(can_use_category[2])
                          ,set(can_use_category[3]),set(can_use_category[4])]
    plane_have_port=[]
    used_prot_heap=[]
    
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        if is_remote[i]:
            continue
        now_intime=plane_in_time[i]
        while len(used_prot_heap)>0 and used_prot_heap[0].outtime<=now_intime:
            top_item=heapq.heappop(used_prot_heap)
            top=top_item.port_num
            if park_country[top]==0 or park_country[top]==2:
                port_canuse_country[0].add(top)
            if park_country[top]==1 or park_country[top]==2:
                port_canuse_country[1].add(top)    
        my_can_use=set() #当前候选机位
        for j in range(plane_category[i],5):#4为种类上限
            my_can_use=my_can_use or port_canuse_category[j]
        my_can_use=my_can_use and port_canuse_country[plane_country[i]]
        my_can_use_list=list(my_can_use)
        
        t=0
        
        for nu in plane_remote_index:
            if i>nu:
                t+=1
    
        now_have_port=wait_check_plane[i-t] #random.randint(0,len(my_can_use)-1)
        
        if not (now_have_port in set(my_can_use_list)):
            # print(i)
            # break
            return False
        
        now_have_finished_time=plane_out_time[i]
        if now_have_port in port_canuse_country[0]:
            port_canuse_country[0].remove(now_have_port)
        if now_have_port in port_canuse_country[1]:
            port_canuse_country[1].remove(now_have_port)
        heapq.heappush(used_prot_heap,P(now_have_port,now_have_finished_time+5/60/24))# 5分钟安全
        plane_have_port.append(now_have_port)
    return True
#%%

def fitness3(plane_have_port, data):
    if not pan(plane_have_port):
        return 1
    values1=0
    zi=0
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_num=plane_have_port[i]
        
        values1+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
        values1+=plane_exit_people[i]*park_exit_walk_time[port_num]
        values1+=plane_passby_people[i]*park_passby_walk_time[port_num]
        
        zi+=plane_arrive_people[i]*park_arrive_walk_time[port_num]*(1-park_is_near[port_num])
        zi+=plane_exit_people[i]*park_exit_walk_time[port_num]*(1-park_is_near[port_num])
        zi+=plane_passby_people[i]*park_passby_walk_time[port_num]*(1-park_is_near[port_num])
    
    return M1*values1/MAXX+M2*zi/values1


#%%
ga = pyeasyga.GeneticAlgorithm(data,
                                population_size=50,
                                generations=50,
                                crossover_probability=0.8,
                                mutation_probability=0.05,
                                elitism=True,
                                maximise_fitness=False)
ga.fitness_function = fitness3               # set the GA's fitness function
ga.create_individual=create_individual
ga.run()

t_fin=time.time()
print("耗时:",t_fin-t_in,"s")


#%%
plane_have_port_best_1=list(ga.best_individual()[1])
for i in plane_remote_index:
    plane_have_port_best_1.insert(i,128)

values_1=0
zi=0
for i in range(0,NUM_OF_PLANE_CALCULATE):
    port_num=plane_have_port_best_1[i]
    
    values_1+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
    values_1+=plane_exit_people[i]*park_exit_walk_time[port_num]
    values_1+=plane_passby_people[i]*park_passby_walk_time[port_num]
    
    zi+=plane_arrive_people[i]*park_arrive_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_exit_people[i]*park_exit_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_passby_people[i]*park_passby_walk_time[port_num]*(1-park_is_near[port_num])

print('ans:',M1*(1-values_1/MAXX)+M2*(1-zi/values_1))

out=[]

for i in range(0,len(plane_have_port_best_1)):
    out.append(num2port[plane_have_port_best_1[i]])

out_index=[ -2 for i in range(0,NUM_OF_PLANE+1)]
for i in range(0,NUM_OF_PLANE):
    out_index[plane_index[i]]=out[i];

print(out_index[1:])

t_fin=time.time()
print("耗时:",t_fin-t_in,"s")

#%% 一个检验

# for i in range(1,NUM_OF_PLANE+1):
#     if out_index[i]==out_index[i+1]:
#         break
# print(i)


print(pan(list(ga.best_individual()[1])))

'''
耗时: 17.738025188446045 s
ans: 0.6732409249153518
[124, 208, 126, 130, 263, 273, 170, 211, 269, 173, 131, 105, 213, 274, 276, 254, 230, 107, 262, 203, 234, 222, 260, 220, 231, 257, 163, 202, 204, 277, 270, 219, 167, 133, 252, 267, 264, 256, 215, 210, 171, 232, 113, 224, 263, 154, 268, 126, 109, 251, 207, 172, 155, 214, 253, 225, 269, 114, 278, 233, 213, 254, 130, 259, 201, 223, 128, 261, 205, 255, 220, 264, 234, 211, 235, 219, 158, 260, 168, 216, 231, 262, 266, 272, 127, 119, 276, 157, 126, 268, 116, 109, 167, 217, 171, 154, 271, 253, 125, 257, 252, 258, 215, 275, 204, 170, 166, 227, 273, 230, 218, 274, 228, 250, 221, 101, 120, 269, 229, 213, 220, 108, 207, 265, 118, 202, 233, 277, 205, 259, 226, 114, 203, 266, 222, 104, 211, 101, 150, 278, 225, 224, 268, 169, 111, 214, 168, 145, 170, 164, 215, 267, 212, 217, 204, 208, 261, 128, 257, 260, 118, 113, 154, 234, 273, 127, 119, 222, 155, 229, 201, 272, 251, 223, 274, 101, 277, 153, 131, 253, 214, 206, 227, 256, 250, 263, 129, 125, 220, 105, 254, 133, 269, 265, 215, 255, 225, 150, 230, 172, 144, 209, 114, 156, 216, 235, 103, 208, 154, 104, 226, 228, 203, 171, 212, 169, -1, 157, 221, 271, 272, 213, 170, 116, 202, 252, 266, 210, 270, 132, 275, 128, 223, 173, 127, 268, 263, 148, 126, 261, 205, 207, 211, 167, 110, 219, 201, 224, 265, 279, 133, 250, 208, 217, 233, 124, 172, 214, -1, 168, 130, 259, 231, 278, 206, 260, 101, 254, 129, 218, 232, 202, 256, 269, 234, 121, 213, 210, 276, 263, 219, 268, 163, 225, 227, 229, 167, 253, 226, 114, -1, 118, 255, 261, 262, 203, 251, 266, 155, 211, 279, 154, 131, 224, 205, 260, 152, -1, 212, 215, 231, 172, 128, 228, 208, 257, 168, 258, 108, 272, 173, 222, 223, 207, 273, 101, 256, 206, 170, 250, 253, 271, 201, 202, 102, 125, 227, 232, 270, 214, 221, 235, 116, 278, 219, 209, 127, 167, 130, 126, 267, 103, 205, 216, 155, 123, 169, 204, 252, 268, 162, 275, 159, 120, 151, 132, 277, 105, 264, 251, 265, 101, -1, -1]
耗时: 17.743813514709473 s

'''