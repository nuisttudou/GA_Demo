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
print(pan(list(ga.best_individual()[1])))

'''
耗时: 19.414661169052124 s
ans: 0.6732571920569154
[130, 257, 172, 253, 208, 274, 210, 269, 209, 203, 155, 110, 217, 262, 212, 259, 268, 149, 265, 218, 205, 219, 277, 131, 172, 233, 170, 264, 232, 211, 275, 254, 173, 235, 201, 169, 261, 214, 271, 204, 164, 229, 171, 167, 220, 251, 260, 125, 156, 226, 221, 133, 128, 168, 202, 278, 127, 112, 262, 205, 258, 206, 276, 223, 256, 267, 126, 231, 277, 218, 232, 272, 268, 211, 209, 224, 116, 215, 257, 208, 259, 216, 219, 212, 250, 123, 221, 155, 225, 128, 103, 104, 269, 253, 122, 125, 201, 228, 274, 252, 130, 132, 255, 133, 202, 120, 168, 129, 222, 264, 267, 172, 275, 235, 266, 173, 106, 229, 265, 127, 126, 101, 262, 204, 114, 273, 203, 268, 263, 224, 261, 162, 250, 218, 216, 149, 233, 109, 157, 276, 279, 220, 251, 227, 113, 131, 167, 104, 211, 108, 133, 207, 205, 217, 266, 213, 173, 212, 221, 228, 114, 105, 209, 268, 172, 272, 164, 270, 158, 259, 127, 230, 273, 130, 208, 101, 278, 165, 125, 275, 155, 223, 132, 229, 215, 225, 255, 204, 252, 103, 233, -1, 269, 216, 226, 210, 169, 119, 250, 261, 114, 274, 120, 154, 257, 207, 102, 212, 201, 113, 131, 129, 172, 266, 217, 262, -1, 104, 231, 253, 279, 224, 251, 171, 254, 221, 205, 258, 267, 230, 235, 214, 206, 219, 215, 276, 255, 106, 256, 203, 209, 270, 167, 126, 159, 128, 211, 213, 208, 261, 222, 216, 132, 210, 260, 269, 250, 154, 202, 263, 264, 129, 232, 227, 223, 229, 112, 218, 171, 127, 234, 169, 275, 204, 225, 105, 226, 273, 265, 212, 252, 209, 156, 130, 133, 207, 217, 205, 173, 117, -1, 113, 278, 211, 168, 264, 224, 255, 125, 270, 262, 214, 231, 124, 208, 216, 151, 250, 154, 267, 128, 274, 233, 273, 169, 127, 147, 220, 152, 268, 172, 277, 276, 204, -1, 159, 126, 259, 258, 256, 254, 235, 269, 130, 101, 201, 218, 217, 272, 203, 264, 279, 123, 266, 208, 129, 202, 230, 229, 205, 131, 166, 125, 222, 212, 101, 107, 171, 232, 234, 114, 219, 109, 153, 108, 223, 257, 164, 228, 231, 221, 132, -1, -1]
耗时: 19.42154550552368 s
True
'''