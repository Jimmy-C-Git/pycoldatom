import numpy as np
from .fithelper import make_fit, make_generate, fit_result_wrap, generate_x, guess_general_2d, mask_bound
import logging
from scipy.optimize import leastsq
from ..utils.exception import Suppressor

logger = logging.getLogger('flowchart.fit_gaussian')

def generate_grids(data):
	x = np.mgrid[[slice(s) for s in data.shape]]

	if hasattr(data, 'mask'):
		x = [np.ma.array(x0, mask=data.mask) for x0 in x]

	return x

def guess_gaussian(data):
	if hasattr(data, 'mask'):
		x0, x1, y0, y1 = mask_bound(data.mask)
	else:
		x1, y1 = data.shape
		x0 = 0
		y0 = 0
	p0 = [1, (x0+x1)/2, (y0+y1)/2, (x1-x0)/4, (y1-y0)/4, 0]
	logger.debug('Initial guess=%s' % p0)
	return p0

def gaussian(grids, n0, x0, y0, rx, ry, offset):
	x, y = grids
	g = n0*np.exp(-(x-x0)**2/(2*rx**2)-(y-y0)**2/(2*ry**2)) + offset
	return g

def error(p, grids, z):
	n0, x0, y0, rx, ry, offset = p
	return gaussian(grids, n0, x0, y0, rx, ry, offset) - z


def fit_gaussian_result(data):
	p0 = guess_gaussian(data)
	grids = generate_grids(data)
	
	grids_compressed = [np.ma.compressed(x0) for x0 in grids]
	data_compressed = np.ma.compressed(data)

	p, cov_x, infodict, mesg, ier = leastsq(error, p0, args=(grids_compressed,data_compressed), full_output=True)
	result = fit_result_wrap(gaussian, p)
	for x in ['rx', 'ry']:
		result[x] = np.abs(result[x])

	result.update(analyse_gaussian(**result))

	if hasattr(data, 'mask'):
		xy = generate_x(data)
		err = gaussian(xy, *p) - data
	else:
		err = infodict['fvec'].reshape(data.shape)
	return result, err


def analyse_gaussian(**kwargs):
	a = {}
	ls = locals()
	ls.update(kwargs)
	s = Suppressor((NameError, KeyError), globals(), ls)
	s("a['total'] = 2 * np.pi * n0 * rx * ry")

	return a