#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 18:05:07 2021

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
NUM_OF_PORT_CALCULATE=128

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



#%% 登机口(机位)下标映射

park_port_set=list(set(park_port))
port2num={} #登机口对应的机位->下标
num2port={} #下标->登机口对应的机位

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

# 判断当前方法是否合法
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
'''
***特别注意***:
目标函数部分plane_have_port中不含远机位的飞机下标，是直接将其删除的
因此需要
for i in plane_remote_index:
    plane_have_port_best_1.insert(i,128)
'''
# 在此次中没有用到的目标函数
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

def fitness1(plane_have_port, data):
    values=0
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_num=plane_have_port[i]
        
        values+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
        values+=plane_exit_people[i]*park_exit_walk_time[port_num]
        values+=plane_passby_people[i]*park_passby_walk_time[port_num]
    
    return values

def fitness2(plane_have_port, data):
    values=0
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_num=plane_have_port[i]
        
        values+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
        values+=plane_exit_people[i]*park_exit_walk_time[port_num]
        values+=plane_passby_people[i]*park_passby_walk_time[port_num]
    zi=0
    zi+=plane_arrive_people[i]*park_arrive_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_exit_people[i]*park_exit_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_passby_people[i]*park_passby_walk_time[port_num]*(1-park_is_near[port_num])
    
    return zi/values

def fitness4(plane_have_port, data):
    port_use_plane_index=[[] for i in range(0,len(park_port_set))]
    
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_use_plane_index[plane_have_port[i]].append(i)

    summ=0
    for port_has_plane_list in port_use_plane_index:
        # this_port_has_plane_num=len(port_has_plane_list)
        plane_free_start_time_list=[8/24]
        plane_free_end_time_list=[]
        for i in port_has_plane_list:
            plane_free_end_time_list.append(plane_in_time[i])
            plane_free_start_time_list.append(plane_out_time[i])
        plane_free_end_time_list.append(24/24)
        
        for i,j in zip(plane_free_start_time_list,plane_free_end_time_list):
            summ+=(i-j)**2        
    
    return summ

def fitness5(plane_have_port, data):
    if not pan(plane_have_port):
        return 1
    S=fitness1(plane_have_port, data)
    E=fitness2(plane_have_port, data)
    f=fitness4(plane_have_port, data)
    S_=1-S/60078/20.59
    F_=(117964800-f)/(117964800)
    return -(0.25*S_+0.6*E+0.15*F_)
    
    
#%%
ga = pyeasyga.GeneticAlgorithm(data,
                                population_size=50,
                                generations=50,
                                crossover_probability=0.8,
                                mutation_probability=0.05,
                                elitism=True,
                                maximise_fitness=False)
ga.fitness_function = fitness5               # set the GA's fitness function
ga.create_individual=create_individual
ga.run()

t_fin=time.time()
print("耗时:",t_fin-t_in,"s")


#%%
plane_have_port_best_1=list(ga.best_individual()[1])

# if not pan(plane_have_port_best_1):
#     print("ERROR")
#输出最佳
S1=fitness1(plane_have_port_best_1, data)
E1=fitness2(plane_have_port_best_1, data)
f1=fitness4(plane_have_port_best_1, data)
S1_=1-S1/60078/20.59
F1_=(117964800-f1)/(117964800)
print("ans:",0.25*S1_+0.6*E1+0.15*F1_)


for i in plane_remote_index:
    plane_have_port_best_1.insert(i,128)

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
耗时: 19.210639476776123 s
ans: 0.20262426218158724
[224, 261, 125, 228, 254, 271, 260, 231, 252, 132, 208, 173, 202, 131, 127, 209, 255, 115, 167, 272, 171, 235, 207, 253, 220, 129, 152, 234, 262, 229, 216, 227, 263, 273, 206, 232, 204, 225, 214, 203, 166, 212, 117, 256, 169, 124, 132, 125, 101, 205, 255, 278, 133, 261, 259, 250, 271, 148, 276, 251, 168, 231, 219, 228, 268, 167, 101, 217, -1, 173, 171, 210, 252, 253, 229, 170, 158, 223, 277, 201, 270, 279, 273, 262, 216, 118, 127, 112, 233, 169, 159, 113, 211, 131, 110, 224, 221, 250, 128, 204, 212, 256, 254, 129, 125, 147, 101, 172, 213, 133, 235, 206, 225, 205, -1, 160, 109, 130, 263, 168, 217, 102, 203, 270, 119, 255, 268, 229, 253, 207, 155, 114, 211, 214, 223, 145, 232, 105, 165, 210, 271, 269, 277, 265, 166, 275, 202, 158, 204, 170, 209, 256, 235, 276, 133, 224, 208, 167, 257, 266, 107, 121, 274, 233, 205, 212, 162, 216, 117, 173, 168, 207, 268, 272, 206, 111, 270, 102, -1, 259, 226, 171, 251, 172, 255, 220, 278, 203, 125, 116, 221, 154, 128, 260, 269, 267, 254, 152, 133, 235, 164, 263, 101, 122, 130, 201, 147, 127, 273, 157, 264, 208, 204, 124, 126, 207, -1, 110, 233, 205, 217, 253, 228, 114, 231, 167, 271, 169, 224, 173, 219, 225, 276, 222, 259, 230, 168, 120, 272, 202, 172, 210, 257, 223, 105, 212, 266, 265, -1, 235, 263, 267, 204, 258, 279, 278, 133, 128, 218, 262, 129, 124, 252, 229, 227, 205, 145, 203, 206, 217, 215, 211, 171, 170, 167, 101, 201, 268, 261, 127, 212, 275, 163, 232, 213, 254, 270, 220, 263, 164, -1, 104, 223, 257, 155, 253, 266, 278, 251, 228, 128, 267, 154, 210, 272, 131, 149, 132, 221, 130, 202, 264, 216, 169, 218, 225, 119, 214, 160, 207, 231, 209, 235, -1, 269, 152, 271, 170, 173, 258, 273, 279, 124, 206, 117, 129, 260, 256, 208, 262, 133, 125, 107, 219, 228, 251, 215, 126, 172, 230, 255, 105, 278, 155, 224, 101, 151, 234, 254, 227, 103, 232, 147, 118, 167, 168, 277, 111, 226, 223, 204, 265, -1, -1]
耗时: 19.21639108657837 s
True
'''
