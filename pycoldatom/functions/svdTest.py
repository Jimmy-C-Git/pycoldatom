import incremental_svd
from incremental_svd import incre_svd
import numpy as np 

incremental_svd.trunc = 1

a = np.mat([[1,1,1,2],[2,2,2,2]])
svd = incre_svd()
next(svd)

print(svd.send(a.flatten().T)) 
b = np.mat([[2,2,2,2],[2,2,2,2]])

print(svd.send(b.flatten().T)) 

