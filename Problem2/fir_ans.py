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
    # print('?')
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
#%%
ga = pyeasyga.GeneticAlgorithm(data,
                                population_size=50,
                                generations=50,
                                crossover_probability=0.8,
                                mutation_probability=0.05,
                                elitism=True,
                                maximise_fitness=False)
ga.fitness_function = fitness1               # set the GA's fitness function
ga.create_individual=create_individual
ga.run()

t_fin=time.time()
print("耗时:",t_fin-t_in,"s")


#%%
plane_have_port_best_1=list(ga.best_individual()[1])
for i in plane_remote_index:
    plane_have_port_best_1.insert(i,128)
values_1=0

for i in range(0,NUM_OF_PLANE):
    port_num=plane_have_port_best_1[i]
    values_1+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
    values_1+=plane_exit_people[i]*park_exit_walk_time[port_num]
    values_1+=plane_passby_people[i]*park_passby_walk_time[port_num]
print('ans:',values_1)

out=[]
for i in range(0,len(plane_have_port_best_1)):
    out.append(num2port[plane_have_port_best_1[i]])

out_index=[ -2 for i in range(0,NUM_OF_PLANE+1)]
for i in range(0,NUM_OF_PLANE):
    out_index[plane_index[i]]=out[i];

print(out_index[1:])

t_fin=time.time()
print("耗时:",t_fin-t_in,"s")

'''
耗时: 6.902955532073975 s
ans: 930699.7999999986
[267, 154, 229, 279, 132, 203, 202, 278, 224, 215, 124, 109, 172, 133, 219, 269, 125, 114, 217, 270, 276, 101, 278, 155, 254, 203, 166, 267, 216, 169, 275, 128, 232, 130, 101, 259, 227, 101, 214, 266, 116, 126, 161, 265, 213, 233, 261, 133, 119, 206, 173, 101, 262, 204, 221, 219, 256, 112, 215, 279, 255, 155, 272, 210, 131, 235, 124, 201, 271, 211, 230, 264, 273, 226, 223, 101, 119, 233, 228, 224, 212, 263, 268, 216, 214, 148, 173, 146, 217, 266, 169, 118, 202, 254, 147, 220, 267, 262, 101, 208, 101, 101, 203, 130, 222, 104, 107, 209, 167, 274, 219, 253, 278, 133, 132, 114, 164, 172, 207, 221, 265, 154, 155, 258, 151, 215, 273, 226, 264, 220, 129, 101, 127, 227, 262, 111, 233, 122, 117, 214, 217, 208, 128, 234, 115, 271, 206, 120, 232, 171, 276, 259, 223, 212, 260, 254, 226, 255, 263, 167, 113, 150, 222, 209, 215, 155, 110, 251, 144, 101, 220, 131, 265, 126, 233, 107, 228, 148, 218, 201, 266, 210, 235, 221, 219, 101, 101, -1, 203, 106, 173, 252, 253, 227, 273, 169, 216, 160, 214, 168, 117, 231, 108, 145, 217, 276, 111, 261, 278, 171, 221, 202, 167, 214, 222, 218, -1, 121, 259, 268, 212, 211, 224, 163, 130, 254, 133, 213, 173, 264, 101, 101, 220, 124, 218, 215, -1, 161, 132, 265, 128, 213, 131, 101, 109, 235, 101, 229, 173, 101, 214, 267, 204, 261, 154, 209, 155, 271, 133, 274, 269, 252, 275, 127, 263, 216, 101, 227, 257, 217, 101, 266, 129, 212, 261, 101, 101, 211, 172, 214, 213, 224, 121, 218, 255, 270, 234, 272, 173, 116, -1, 115, 217, 133, 170, 205, 101, 258, 221, 272, 218, 254, 265, 210, 264, 265, 114, 211, 202, 220, 270, 273, 201, 258, 201, 101, 101, 262, 115, 233, 204, 223, 268, 234, 101, 114, 101, 133, 126, 155, 212, 269, 203, 126, 111, 221, 231, 172, 132, 101, 205, 101, 103, 215, 201, 275, 214, 228, 266, 278, 167, 118, 219, 208, 271, 121, 117, 265, 222, 223, 153, 262, 152, 123, 109, 234, 155, 118, 202, 221, 128, 260, -1, -1]
'''