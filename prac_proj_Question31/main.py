#! /usr/bin/env python 
#-*- coding: utf:8 -*- 

import numpy as np 
from itertools import permutations

def gen_list(n):
	s = np.arange(1,n+1)
	List = list(permutations(s))
	return List
	

def per_list(l):
	print('origin',l)

	for i in range(len(l)):
		val = l[i]
		if val != (i + 1):
			l[val-1],l[i] = l[i],l[val-1]
		else:
			l[i] = l[i]
	return l
	

n = 5
KK = gen_list(n)
db_list = []
for j in range(len(KK)):
	tmp_list = list(KK[j])
	if per_list(tmp_list) == range(1,n+1,1):
		pass
	else:
		db_list.append(tmp_list)

print(len(db_list))

	
	
