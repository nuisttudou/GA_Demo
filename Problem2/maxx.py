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
                                population_size=500,
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
耗时: 214.58194947242737 s
ans: 0.6770579531951816
[269, 213, 209, 201, 133, 215, 211, 128, 202, 228, 230, 101, 274, 278, 265, 229, 169, 153, 131, 235, 266, 257, 220, 253, 132, 272, 165, 213, 256, 204, 207, 273, 124, 201, 255, 125, 218, 168, 234, 211, 157, 203, 109, 130, 230, 126, 128, 254, 151, 221, 261, 202, 260, 263, 232, 219, 265, 101, 173, 266, 250, 253, 267, 209, 133, 252, 231, 225, 132, 258, 207, 268, 278, 269, 218, 277, 149, 234, 205, 208, 274, 228, 201, 169, 254, 102, 224, 160, 262, 213, 112, 158, 272, 273, 110, 127, 256, 130, 223, 214, 227, 270, 259, 226, 219, 163, 111, 222, 215, 129, 173, 171, 170, 266, 255, 157, 101, 269, 204, 172, 265, 120, 155, 210, 116, 233, 278, 234, 232, 251, 261, 122, 203, 225, 127, 168, 202, 101, 113, 223, 212, 227, 263, 264, 156, 274, 206, 108, 271, 144, 131, 154, 256, 268, 259, 229, 267, 209, 215, 204, 168, 123, 228, 231, 273, 233, 104, 272, 109, 201, 130, 173, 170, 255, 172, 161, 133, 164, 171, 210, 230, 254, 222, 258, 278, 260, 276, 167, 211, 114, 226, 275, 216, 207, 212, 257, 205, 166, 261, 264, 123, 203, 158, 101, 221, 225, 153, 168, 234, 160, 206, 217, 131, 224, 271, 219, -1, 120, 155, 267, 214, 251, 229, 103, 252, 215, 227, 124, 268, 263, 213, 259, 202, 262, 278, 231, 235, 115, 126, 274, 272, 220, 253, 170, 112, 204, 203, 201, 230, 167, 273, 275, 261, 169, 269, 226, 154, 210, 127, 232, 279, 217, 125, 270, 233, 227, 121, 254, 221, 267, 132, 215, 211, 264, 234, 101, 260, 274, 265, 224, 133, 222, 110, 276, 223, 251, 209, 268, 219, 159, -1, 102, 275, 216, 128, 154, 173, 252, 258, 230, 250, 203, 214, 278, 255, 169, -1, 226, 217, 259, 221, 261, 167, 155, 211, 257, 163, 129, 152, 225, 168, 218, 213, 260, 171, 112, 274, 266, 277, 125, 234, 262, 124, 210, 162, 256, 209, 133, 208, 279, 233, 216, 156, 126, 263, 224, 228, 229, 220, 221, 212, 109, 276, 128, 259, 121, 144, 253, 215, 235, 118, 232, 113, 170, 101, 273, 207, 101, 130, 275, 202, 101, -1, -1]
耗时: 214.5886514186859 s
True
'''
