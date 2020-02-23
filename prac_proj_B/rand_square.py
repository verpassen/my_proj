#!/usr/bin/env python
#-*- coding: utf:8 -*-

import random
import numpy as np 
from math import sqrt 

def create_rand_list(a,b):
	# b should be an interger
	t = range(0,b)
	ind = random.sample(list(a),len(t))
	return ind

def create_rand_sqr(n):
    N = n**2
    P = int(sqrt(N))
    L1 = np.linspace(1,N,N)
    ran_L1 = random.sample(list(L1),len(L1))
    A = np.reshape(ran_L1,(P,P))
    return A

def check_line(L,square):
	pos = {}
	x,y,s = 0,0,0
	len_x, len_y = square.shape[0],square.shape[1]
	C = np.zeros((len_x,len_y))
	for k in L:
		pos=np.where(square==k,1,0)
		C = C+ pos
	for k in range(len_x):
		if np.sum(C[:,k])> len_x-1:
			s = s+1
			#print('there is a connection in col',s)
	for k in range(len_y):
		if np.sum(C[k,:])> len_y-1:
			s = s+1
			#print('there is a connection in row',s)
	if np.sum(np.diag(C)) > len_x -1:
		s = s+1
		#print('there is one line in diag',s)
	else:
		step = len(C)-1
		sum_C = np.sum(np.take(C,np.arange(step,C.size-1,step)))
		if sum_C > len_x-1:
			s = s +1
			#print('there is a connection in diag',s)

	return C,s

