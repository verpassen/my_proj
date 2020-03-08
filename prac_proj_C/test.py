import numpy as np

a = np.zeros([4,4]).astype(int)
#specify the position 
a[1][2] = 1 
a[3][0] = 1

#a =np.asarray([[1,0,1,0],[0,1,0,0],[0,0,0,0]])

def rev_val(k,p):
	x,y = p[0],p[1]
	len_x ,len_y = len(k[:,0]),len(k[0,:])
	if (x+1) <= (len_x-1):
		k[x+1][y] = (k[x+1][y]) ^ (k[x][y])			
	if (x-1) >= 0:	
		k[x-1][y] = (k[x-1][y]) ^ (k[x][y])			
	if (y-1) >= 0:
		k[x][y-1] = (k[x][y-1]) ^ (k[x][y])			
	if (y+1) <= len_y-1:	
		k[x][y+1] = (k[x][y+1]) ^ (k[x][y])			
	
	k[x][y] = 0	
	S = k
	return S

a=rev_val(a,[0,0])
print(a)	
print(rev_val(a,[0,2]))

