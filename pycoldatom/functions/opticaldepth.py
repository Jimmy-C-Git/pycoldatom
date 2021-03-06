import numpy as np

def calculateOD(sig, ref, bkg):
	if bkg is not None:
		sig = sig - bkg
		ref = ref - bkg
	min_step = 1
	mask = np.logical_or(sig<=0, ref<=0)
	sig = np.maximum(sig, min_step)
	ref = np.maximum(ref, min_step)
	od = (-np.log(sig/ref)).astype('f4')
	od_0 = np.copy(od)
	od_0[mask] = 0
	return od, od_0