#!/usr/bin/env python
#-*- coding:utf:8 -*-
import numpy as np 
from itertools import permutations
import time 
# method 1 
def method_stair(n):
    if n <= 2:
        x = n
    else: 
        x = method_stair(n-1)+ method_stair(n-2)        
    return x
# method 2
def method_stair2(n,l=[1,2]):
    if n<=2:
        return l[n-1]
    else:
        for i in range(len(l),n):
            l.append(l[i-1]+l[i-2])
    return l[n-1]


if '__name__' == '__main__':
    t = time.time()
    print(method_stair(30))
    elapsed = time.time() - t 

    tt = time.time()
    print(method_stair2(50))
    elapsed2 = time.time() - tt 

    print('time1 v.s. time2 ',elapsed , elapsed2)


