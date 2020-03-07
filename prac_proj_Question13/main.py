#! /usr/bin/env python
#-*- coding: utf:8 -*-
#J
import numpy as np 
from itertools import permutations 

def init():
	set = {}
	seq = range(30)
	for k in seq:
		set[k+1]=[] 
	return set 

def gen_list(s):
	#l = np.arange(1,s+1)
	l = [k for k in range(1,s+1)]
	List = list(permutations(l,len(l))) 
	return List

def rev_process(List_A):
	tmp_b =[]
	# without "tmp_b=[]"
	# UnboundLocalError: local variable 'tmp_b' referenced before assignment
	
	if List_A[0] == 1 :
		tmp_b = List_A
	else:
		qty = List_A[0]-1
		tmp_b = List_A[qty::-1]+List_A[qty+1:]
	return tmp_b

S = init()
tmp = gen_list(9)
len_list = len(tmp)

for k in range(len_list):
	#print('origin list', tmp[k])
	j = 1
	rev_tmp = rev_process(tmp[k])
	#print(rev_tmp) 
	while rev_tmp[0] != 1:
		rev_tmp = rev_process(rev_tmp)	
		#print(rev_tmp)
		j = j + 1
	else:
		S[j].append([tmp[k]])
		
print(len(S[5]))

	
	



