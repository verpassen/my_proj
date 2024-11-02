#!/usr/bin/env python 
#-*- coding: utf:8 -*-

import random 
import numpy as np 
from rand_square import * 

n = 6 
sampling_qty = 15 
Test_times = 10000
List_A = np.arange(1,6**2+1)
Record,times = np.zeros(Test_times),0

for k in range(Test_times):
    Rand_list = sorted(create_rand_list(List_A,sampling_qty))
    Square_A = create_rand_sqr(n)
    C,s= check_line(Rand_list,Square_A)
    Record[k] = s 
    if (s >= 1):
        times = times +1 

print(times)
print('probability',times/Test_times)
#=======check =============#
#print('Square\n',Square_A)
#print('List\n',Rand_list)
#print(C)
#print(s)

#==============


 





