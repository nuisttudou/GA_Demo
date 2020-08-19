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

# Cfi=np.array(info_data_in['机位型']).astype(int)
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


#%%
# indexx=list(range(0,NUM_OF_G))
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

# can_use_country=[]

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
# can_use_country[2]=[]
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
    # x=np.zeros(( NUM_OF_PLANE,NUM_OF_G))
    
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
        
        
        # if plane_out_time[i]-plane_in_time[j]>=6/24: #6h 直接停远机位
        #     now_have_port=128 #128为远位
        # else: #在普通机位和远机位选一个
        my_can_use_list=list(my_can_use)
        
        # print(i)
        now_have_port_index=random.randint(0,len(my_can_use)-1)
        now_have_port=my_can_use_list[now_have_port_index]
        
        now_have_finished_time=plane_out_time[i]
        
        # plane_have_port.append((i,now_have_port))
        
        if now_have_port in port_canuse_country[0]:
            port_canuse_country[0].remove(now_have_port)
        if now_have_port in port_canuse_country[1]:
            port_canuse_country[1].remove(now_have_port)
        
        heapq.heappush(used_prot_heap,P(now_have_port,now_have_finished_time+5/60/24))# 5分钟安全
        
        plane_have_port.append(now_have_port)
        # x[i][now_have_port]=1;
        
        
    return plane_have_port
        # x=x.astype(int).flatten().tolist()
        # return x

#%%
def fitness1(plane_have_port, data):
    values=0
    # print('!')
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_num=plane_have_port[i]
        
        values+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
        values+=plane_exit_people[i]*park_exit_walk_time[port_num]
        values+=plane_passby_people[i]*park_passby_walk_time[port_num]
    
    return values

def fitness2(plane_have_port, data):
    values=0
    zi=0
    # print('?')
    for i in range(0,NUM_OF_PLANE_CALCULATE):
        port_num=plane_have_port[i]
        
        values+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
        values+=plane_exit_people[i]*park_exit_walk_time[port_num]
        values+=plane_passby_people[i]*park_passby_walk_time[port_num]
    
        zi+=plane_arrive_people[i]*park_arrive_walk_time[port_num]*(1-park_is_near[port_num])
        zi+=plane_exit_people[i]*park_exit_walk_time[port_num]*(1-park_is_near[port_num])
        zi+=plane_passby_people[i]*park_passby_walk_time[port_num]*(1-park_is_near[port_num])
    
    return zi/values




#%%
ga2 = pyeasyga.GeneticAlgorithm(data,
                                population_size=50,
                                generations=50,
                                crossover_probability=0.8,
                                mutation_probability=0.05,
                                elitism=True,
                                maximise_fitness=False)
ga2.fitness_function = fitness2               # set the GA's fitness function
ga2.create_individual=create_individual
ga2.run()

print(ga2.best_individual()[0])
t=np.array(ga2.best_individual()[1])
print(t)

#%%
print("ga-answer:",ga2.best_individual()[0])
plane_have_port_best_2=list(ga2.best_individual()[1])

for i in plane_remote_index:
    plane_have_port_best_2.insert(i,128)

values_best_2=0
zi=0
# print('?')
for i in range(0,NUM_OF_PLANE):
    port_num=plane_have_port_best_2[i]
    
    values_best_2+=plane_arrive_people[i]*park_arrive_walk_time[port_num]
    values_best_2+=plane_exit_people[i]*park_exit_walk_time[port_num]
    values_best_2+=plane_passby_people[i]*park_passby_walk_time[port_num]

    zi+=plane_arrive_people[i]*park_arrive_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_exit_people[i]*park_exit_walk_time[port_num]*(1-park_is_near[port_num])
    zi+=plane_passby_people[i]*park_passby_walk_time[port_num]*(1-park_is_near[port_num])

print('ans:',1-zi/values_best_2)
print(plane_have_port_best_2)




#%%
t_fin=time.time()
print("耗时:",t_fin-t_in,"s")