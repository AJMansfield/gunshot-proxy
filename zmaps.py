import numpy as np
from numpy import array
from scipy.interpolate import interp1d

zmaps = {}

elz = array([(60, 0), (50, 20), (40, 40), (30, 60), (20, 80), (10, 100), (0, 120)], dtype=[('x', float), ('y', float)])
elz.sort(axis=0, order='x')
x, y = elz['x'], elz['y']
f = interp1d(x, y, bounds_error=False, fill_value=(y[0], None), assume_sorted=True)
for num in [1, 2, 3, 4, 5, 6]:
    zmaps[f'bosch{num}'] = f

elz = array([(60, 0), (50, 10), (40, 20), (30, 30), (20, 40), (10, 50), (0, 40)], dtype=[('x', float), ('y', float)])
elz.sort(axis=0, order='x')
x, y = elz['x'], elz['y']
f = interp1d(x, y, bounds_error=False, fill_value=(y[0], None), assume_sorted=True)
for num in [7, 8, 9, 14, 15]:
    zmaps[f'bosch{num}'] = f

f = np.vectorize(lambda x: np.NaN)
for num in [10, 11, 12, 16, 17, 18]:
    zmaps[f'bosch{num}'] = f