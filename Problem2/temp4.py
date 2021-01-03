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


port_canuse_country=[set(can_use_country[0]),set(can_use_country[1])]
port_canuse_category=[[],set(can_use_category[1]),set(can_use_category[2])
                      ,set(can_use_category[3]),set(can_use_category[4])]

port_equal_above_can_use=[set(),set(),set(),set(),set()]
port_equal_above_can_use[4]=port_canuse_category[4]
for i in [3,2,1]:
    port_equal_above_can_use[i]=port_canuse_category[i] | port_equal_above_can_use[i+1]



#%% 远机位
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
    # port_canuse_category=[[],set(can_use_category[1]),set(can_use_category[2])
    #                       ,set(can_use_category[3]),set(can_use_category[4])]
    plane_have_port=[]
    used_prot_heap=[]
    
    plane_use_rear_index=[]
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
        
        # my_can_use=set() #当前候选机位
        # for j in range(plane_category[i],5):#4为种类上限
        #     my_can_use=my_can_use or port_canuse_category[j]
        my_can_use=port_equal_above_can_use[plane_category[i]]
        
        my_can_use=my_can_use & port_canuse_country[plane_country[i]]
        my_can_use_list=list(my_can_use)
        
        # print(i,":",len(my_can_use))
        if len(my_can_use)==0:
            plane_use_rear_index.append(i)
            continue
        
        now_have_port_index=random.randint(0,len(my_can_use)-1)
        now_have_port=my_can_use_list[now_have_port_index]
        now_have_finished_time=plane_out_time[i]
        if now_have_port in port_canuse_country[0]:
            port_canuse_country[0].remove(now_have_port)
        if now_have_port in port_canuse_country[1]:
            port_canuse_country[1].remove(now_have_port)
        heapq.heappush(used_prot_heap,P(now_have_port,now_have_finished_time+5/60/24))# 5分钟安全
        plane_have_port.append(now_have_port)
        
    for i in plane_use_rear_index:
        plane_have_port.insert(i,128)
    return plane_have_port

#%%

M1=0.36
M2=0.64
MAXX=60078*20.58


def pan(wait_check_plane):
    port_canuse_country=[set(can_use_country[0]),set(can_use_country[1])]
    # port_canuse_category=[[],set(can_use_category[1]),set(can_use_category[2])
    #                       ,set(can_use_category[3]),set(can_use_category[4])]
    plane_have_port=[]
    used_prot_heap=[]
    
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        if is_remote[i] or wait_check_plane[i]==128:
            continue
        now_intime=plane_in_time[i] 
        while len(used_prot_heap)>0 and used_prot_heap[0].outtime<=now_intime:
            top_item=heapq.heappop(used_prot_heap)
            top=top_item.port_num
            if park_country[top]==0 or park_country[top]==2:
                port_canuse_country[0].add(top)
            if park_country[top]==1 or park_country[top]==2:
                port_canuse_country[1].add(top)    
                
        # my_can_use=set() #当前候选机位
        # for j in range(plane_category[i],5):#4为种类上限
        #     my_can_use=my_can_use or port_canuse_category[j]
        my_can_use=port_equal_above_can_use[plane_category[i]]
        my_can_use=my_can_use & port_canuse_country[plane_country[i]]
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
# for cp in [0.6,0.7,0.8]:
    

#     ga = pyeasyga.GeneticAlgorithm(data,
#                                     population_size=50,
#                                     generations=50,
#                                     crossover_probability=0.8,
#                                     mutation_probability=0.05,
#                                     elitism=True,
#                                     maximise_fitness=False)
#     ga.fitness_function = fitness3               # set the GA's fitness function
#     ga.create_individual=create_individual
#     ga.run()




#%%
plane_have_port_best_1=[]
fit_maxx=0
for i in range(0,500):
    now_port_list=create_individual([])
    fit_now=fitness3(now_port_list,[])
    if fit_maxx<fit_now:
        fit_maxx=fit_now
        plane_have_port_best_1=create_individual([])
    
t_fin=time.time()
print("耗时:",t_fin-t_in,"s")

# plane_have_port_best_1=list(ga.best_individual()[1])
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
# print(pan(list(ga.best_individual()[1])))

'''
耗时: 17.361228704452515 s
ans: 0.6608875621970746
[228, 167, 264, 235, -1, 201, 254, 274, 169, 126, 225, 170, 255, 221, 130, 223, 230, 156, 278, 253, 232, 218, 127, 215, 203, 224, 171, 264, 231, 217, 210, 228, 207, 209, 270, 205, 128, 261, 213, 167, 117, 235, 110, 133, 256, 234, 155, 172, 118, 229, 261, 201, 255, 267, 216, 132, 278, 168, 258, 220, 271, 266, 219, 202, 130, 221, 259, 170, 269, 225, 270, 169, 227, 265, 207, 204, 107, 274, 277, 222, 217, 233, 268, 208, 235, 152, 273, 119, 209, 203, 122, 163, 131, 275, 160, 133, 167, 251, 252, 173, 171, 214, 230, 256, 250, 101, 110, 154, 257, 212, 201, 254, 125, 155, 234, 158, 166, 260, 126, 168, 221, 102, 279, 235, 162, 233, 276, 229, 258, 226, 129, 116, -1, 128, 207, 103, 132, 101, 111, 218, 263, 232, 205, 262, 105, 210, 208, 171, 125, 115, 256, 169, 214, 170, 225, 271, 211, 222, 204, 172, 112, 106, 270, 251, 269, 235, 146, 279, 151, 203, 129, 201, 219, 272, 127, 101, 258, 120, 124, 266, 217, 230, 265, 206, 207, 277, 213, 167, 215, 159, 229, 231, 220, 228, 211, 257, 221, 166, 225, 168, 121, 267, 156, 117, 172, 271, 171, 232, 253, 152, 208, 226, 274, 279, 209, 216, -1, 123, 126, 154, 275, 263, 130, 114, 218, 173, 222, 260, 204, 132, 131, 250, 125, 268, 224, 201, 251, 107, 233, 129, 207, 210, 133, 203, 170, 206, 259, 235, 265, 230, 228, 172, 267, 269, 128, 231, 253, 264, 254, 155, 212, 275, 227, 278, 219, 132, 118, 277, 154, 209, 202, 204, 217, 279, 208, 156, 213, 125, 234, 224, 260, 215, 146, 251, 270, 167, 274, 207, 226, 166, -1, 109, 265, 133, 205, 254, 253, 212, 273, 218, 263, 128, 169, 266, 155, 172, -1, 203, 271, 127, 227, 259, 262, 230, 208, 228, 101, 261, 160, 168, 201, 276, 202, 251, 252, 162, 274, 213, 129, 225, 204, 126, 235, 170, 120, 207, 233, 270, 229, 216, 226, 254, 157, 124, 221, 267, 132, 130, 264, 224, 171, 107, 206, 214, 222, 101, 165, 232, 257, 125, 110, 278, 105, 106, 148, 154, 255, 145, 211, 220, 256, 273, -1, -1]
耗时: 17.367674827575684 s
True
'''