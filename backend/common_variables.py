import ahrs
import numpy as np



GM = 3.986005*10**14
we = 7.2921151467 *10**(-5) 
c = 299792458

wgs = ahrs.utils.WGS()

#romsdalen
phi = 62.47714 * np.pi/180
lam = 7.772829 * np.pi/180
h = 60.7

#romsdalen på veg
N = 6948183.94
E = 127961.24
h = 60.7
#Parkeringsplass NTNU 20 grader
# phi = 63.41457900 * np.pi/180
# lam = 10.41045326 * np.pi/180
# h = 42.738

#Parkeringsplass NTNU 10 grader
# phi = 63.41458293  * np.pi/180
# lam = 10.41044691  * np.pi/180
# h =39.689


T = np.matrix([[-np.sin(phi)*np.cos(lam),-np.sin(phi)*np.sin(lam) , np.cos(phi)], 
            [-np.sin(lam), np.cos(lam), 0],
            [np.cos(phi)*np.cos(lam), np.cos(phi)*np.sin(lam), np.sin(phi)]])
