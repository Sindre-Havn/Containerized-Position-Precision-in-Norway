import multiprocessing

from multiprocessing.managers import SharedMemoryManager
from time import sleep, perf_counter_ns
import pickle

from computeDOP import create_observers, find_dop_on_point

import resource
import sys

import functools

from dataclasses import dataclass

import json

"""import os
import psutil
def get_script_memory_usage():
    #Returns the resident set size (RSS) memory usage of the current Python script
    #in megabytes (MB).
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    # RSS is the non-swapped physical memory a process has used.
    # Convert bytes to megabytes.
    return mem_info.rss / (1024 * 1024)
"""


"""
# Data successfully passed to function
def dop(a, b, shared_data):
    print('entered, -point', shared_data[4][a])
    sleep(10)
    print('exit')
    #return a * b

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
    with multiprocessing.Pool(processes=4) as pool:
        steps = [(1, 2,shared_data), (3, 4, shared_data), (5, 6, shared_data)]
        results = pool.starmap(dop, steps)
    
    print(results)  # Output: [2, 12, 30]
"""

"""
# Successfully run in parallell, think it takes a lot of time to open files
def dop(step):
    print('Enter', step)
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

if __name__ == '__main__':
    #shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
    with multiprocessing.Pool(processes=5) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]
"""

"""
# Somewhat faster using gloabl variables, and only opening the file once. tid 1:19, 7 core, 7 GB
def dop(step):
    global shared_data
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
    with multiprocessing.Pool(processes=7) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]

"""

"""
# Somewhat faster using gloabl variables, and only opening the file once. 7 core, tid 1:17, 13 GB minne
def dop(step):
    global shared_data
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
    manager=multiprocessing.Manager()
    shared_data=manager.list(shared_data)
    with multiprocessing.Pool(processes=7) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]
"""

"""
# Somewhat faster using gloabl variables, and only opening the file once. 5 kjerner, tid 1:10, 13 GB minne, chunksize=> raskere
def dop(shared_data, step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
        shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
        #shared_data = multiprocessing.shared_memory.SharedMemory(create=True, size=sys.getsizeof(shared_data))
    manager=multiprocessing.Manager()
    shared_data=manager.list(shared_data)
    gen_func = functools.partial(dop, shared_data)
    with multiprocessing.Pool(processes=5) as pool:
        steps = [i for i in range(100)]
        results = pool.imap_unordered(gen_func, steps, chunksize=2)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]
"""
"""
# tid 10:01, 7 cores, hele settet. chunksize=5
def dop(step):
    global shared_data
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = [gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper]
    with multiprocessing.Pool(processes=7) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=5)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]
"""



"""

# tid 9:46, 7 cores, hele settet. chunksize=5, lagt til init med read only class

class Read_Only:
    def __init__(self, value):
        self._read_only_attribute = value
    @property
    def glob_var(self):
        # This method acts as the getter for the read-only attribute
        return self._read_only_attribute

def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data
    shared_data = shared_data.glob_var

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    shared_data = Read_Only(shared_data)
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=5)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]

"""

"""
# tid 9:37, 7 cores, hele settet. chunksize=5, lagt til init med read only class
class Read_Only:
    def __init__(self, value):
        self._read_only_attribute = value
    @property
    def glob_var(self):
        # This method acts as the getter for the read-only attribute
        return self._read_only_attribute

def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.glob_var
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    shared_data = Read_Only(shared_data)
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=5)
        for r in results:
            print(r)
    
    print(results)  # Output: [2, 12, 30]
"""

"""
# tid 9:15, 7 cores, hele settet. chunksize=7, lagt til init med read only class
class Read_Only:
    def __init__(self, value):
        self._read_only_attribute = value
    @property
    def glob_var(self):
        # This method acts as the getter for the read-only attribute
        return self._read_only_attribute

def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.glob_var
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    shared_data = Read_Only(shared_data)
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=7)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    
    print(results)  # Output: [2, 12, 30]
"""


"""
    # tid 9:05, 7 cores, hele settet. chunksize=14, lagt til init med read only class
class Read_Only: # Consider using frozen dataclass
    def __init__(self, value):
        self._read_only_attribute = value
    @property
    def glob_var(self):
        # This method acts as the getter for the read-only attribute
        return self._read_only_attribute

def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.glob_var
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    shared_data = Read_Only(shared_data)
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=14)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    
    print(results)  # Output: [2, 12, 30]

"""

"""
# 7:23, 7 cores, chunksize=14, 100 punkt

start = perf_counter_ns()
def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    @dataclass(frozen=True)
    class Read_Only:
        data = shared_data
    shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=14)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

"""

"""
# 7:06, 7 cores, chunksize=1, 100 punkt

start = 0
def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        data = shared_data
    shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=1)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

"""


"""
# 

start = 0
def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.data
    #print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    #print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    #print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    @dataclass(frozen=True)
    class Read_Only:
        data = shared_data
    shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
            steps = [i for i in range(100)]
            results = pool.imap(dop, steps, chunksize=1)
            for r in results:
                pass
    for i in range(5):
        start = perf_counter_ns()
        with multiprocessing.Pool(processes=7, initializer=init) as pool:
            steps = [i for i in range(100)]
            results = pool.imap(dop, steps, chunksize=1)
            for r in results:
                pass
                #print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
        print('imap: ', (perf_counter_ns()-start)/1_000_000_000)
        print(results)  # Output: [2, 12, 30]
    
    for i in range(5):
        start = perf_counter_ns()
        with multiprocessing.Pool(processes=7, initializer=init) as pool:
            steps = [i for i in range(100)]
            results = pool.imap_unordered(dop, steps, chunksize=1)
            for r in results:
                pass
                #print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
        print('imap_unordered: ', (perf_counter_ns()-start)/1_000_000_000)
        print(results)  # Output: [2, 12, 30]

"""

"""

start = 0
def dop(step):
    global RO
    #print('Enter', step)
    find_dop_on_point(RO.dem_data, RO.gnss_mapping, RO.gnss, RO.time, RO.points[step], RO.observers[step], RO.observers_cartesian[step], RO.elevation_angle, RO.E_lower, RO.N_upper, step)
    #print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    #print('Process ID', multiprocessing.current_process())
    return step

def init():
    global RO

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        gnss_mapping = gnss_mapping
        gnss = gnss
        time = time
        elevation_angle = elevation_angle
        points = points
        dem_data = dem_data
        observers = observers
        observers_cartesian = observers_cartesian
        E_lower = E_lower
        N_upper = N_upper
    RO = Read_Only()
    del gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper
    with multiprocessing.Pool(processes=7) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=1)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

"""


"""
# 7:06, 7 cores, chunksize=1, 100 punkt

start = 0
def dop(step):
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = shared_data.data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        dem_data = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper)
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        data = shared_data
    shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=1)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

"""



"""
start = 0

def temp():
    pass


def run_conccurently(func, args, processes_cnt = 1):
    results = []
    @dataclass(frozen=True)
    class Read_Only:
        data = args
    global RO
    RO = Read_Only()
    del args
    def init():
        global RO
    def dop(step):
        global RO
        #print('Enter', step)
        #find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
        print([type(i) for i in (*RO.data, step)])
        find_dop_on_point(*RO.data, step)
        #print('Exit', step)
        #initial_memory = get_script_memory_usage()
        #print(f"Initial memory usage: {initial_memory:.2f} MB")
        #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
        #print('Process ID', multiprocessing.current_process())
        return step
    start = perf_counter_ns()
    with multiprocessing.Pool(processes=processes_cnt, initializer=init) as pool:
        steps = [i for i in range(100)]
        results_generator = pool.imap(dop, steps, chunksize=1)
        for r in results_generator:
            results.append(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

processes_cnt = 7
if __name__ == '__main__':
    gnss_mapping, gnss, time, elevation_angle, points, dem_data, observers, observers_cartesian, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        dem_data = pickle.load(inp)
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        points = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = [dem_data, gnss_mapping, gnss, time, elevation_angle, points, observers, observers_cartesian, E_lower, N_upper]
    #run_conccurently(temp, shared_data, 7)

    args = shared_data
    results = []
    @dataclass(frozen=True)
    class Read_Only:
        data = args
    global RO
    RO = Read_Only()
    del args
    def init():
        global RO
    def dop(step):
        global RO
        #print('Enter', step)
        #find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
        print([type(i) for i in (*RO.data, step)])
        find_dop_on_point(*RO.data, step)
        #print('Exit', step)
        #initial_memory = get_script_memory_usage()
        #print(f"Initial memory usage: {initial_memory:.2f} MB")
        #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
        #print('Process ID', multiprocessing.current_process())
        return step
    start = perf_counter_ns()
    with multiprocessing.Pool(processes=processes_cnt, initializer=init) as pool:
        steps = [i for i in range(100)]
        results_generator = pool.imap(dop, steps, chunksize=1)
        for r in results_generator:
            results.append(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]
"""


"""

start = 0
def dop(step):
        dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = shared_data.data
        print('Enter', step)
        find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
        print('Exit', step)
        #initial_memory = get_script_memory_usage()
        #print(f"Initial memory usage: {initial_memory:.2f} MB")
        print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
        print('Process ID', multiprocessing.current_process())
        return step


def main():
    if __name__ == '__main__':
        dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
        with open('multiprocessing_test.pkl', 'rb') as inp:
            dem_data = pickle.load(inp)
            gnss_mapping = pickle.load(inp)
            gnss = pickle.load(inp)
            time = pickle.load(inp)
            points = pickle.load(inp)
            observers = pickle.load(inp)
            observers_cartesian = pickle.load(inp)
            elevation_angle = pickle.load(inp)
            E_lower = pickle.load(inp)
            N_upper = pickle.load(inp)
        
        shared_data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
        def init():
            global shared_data
        start = perf_counter_ns()
        @dataclass(frozen=True)
        class Read_Only:
            data = shared_data
        shared_data = Read_Only()
        

        with multiprocessing.Pool(processes=7, initializer=init) as pool:
            steps = [i for i in range(100)]
            results = pool.imap(dop, steps, chunksize=1)
            for r in results:
                print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
        print(perf_counter_ns()-start)
        print(results)  # Output: [2, 12, 30]

if __name__ == '__main__':
    main()
"""

"""
# 7:06, 7 cores, chunksize=1, 100 punkt

start = 0
def dop(step):
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = shared_data.data
    print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    print('Process ID', multiprocessing.current_process())
    return step

def init():
    global shared_data

if __name__ == '__main__':
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        dem_data = pickle.load(inp)
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        points = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    shared_data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        data = shared_data
    shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=1)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]
"""

"""
# 6:44, 7 cores, chunksize=1, 100 samples. Freshly started comupter
start = 0
def dop(step):
    global shared_data
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = shared_data.data
    #print('Enter', step)
    find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    #print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    #print('Process ID', multiprocessing.current_process())
    return step



def main(data):
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        data = data
    def init():
        global shared_data
        shared_data = Read_Only()
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(100)]
        results = pool.imap(dop, steps, chunksize=1)
        for r in results:
            print(r) # Kan vurdere å yielde her, ikke selve verdien (prosenten), men bare detektere at en ny er ferdig
    print(perf_counter_ns()-start)
    print(results)  # Output: [2, 12, 30]

if __name__ == '__main__':
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_test.pkl', 'rb') as inp:
        dem_data = pickle.load(inp)
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        points = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
    main(data)
"""


# 7:44, 7 cores, chunksize=1, 100 samples. somewhat freshly started comupter
start = 0
def dop(step):
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = shared_data.data
    #print('Enter', step)
    return find_dop_on_point(dem_data, gnss_mapping, gnss, time, points[step], observers[step], observers_cartesian[step], elevation_angle, E_lower, N_upper, step)
    #print('Exit', step)
    #initial_memory = get_script_memory_usage()
    #print(f"Initial memory usage: {initial_memory:.2f} MB")
    #print(f"Initial memory usage: {(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1000):.2f} MB")
    #print('Process ID', multiprocessing.current_process())



def main(data):
    start = perf_counter_ns()
    @dataclass(frozen=True)
    class Read_Only:
        data = data
    def init():
        global shared_data
        shared_data = Read_Only()
    step = 0
    dop_list = []
    with multiprocessing.Pool(processes=7, initializer=init) as pool:
        steps = [i for i in range(1,105)]
        total_steps = len(steps)-1
        result_generator = pool.imap(dop, steps, chunksize=1)
        for r in result_generator:
            dop_list.append(r)
            step += 1
            yield f"{int((step / total_steps) * 100)}\n\n"
    dt = (perf_counter_ns()-start)/10**9/60
    print(f'{int(dt)}:{int((dt-int(dt))*60)}')
    #print(results)  # Output: [2, 12, 30]
    yield f"{json.dumps(dop_list)}\n\n"

if __name__ == '__main__':
    dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper = None, None, None, None, None, None, None, None, None, None
    with open('multiprocessing_dop_testdata.pkl', 'rb') as inp:
        dem_data = pickle.load(inp)
        gnss_mapping = pickle.load(inp)
        gnss = pickle.load(inp)
        time = pickle.load(inp)
        points = pickle.load(inp)
        observers = pickle.load(inp)
        observers_cartesian = pickle.load(inp)
        elevation_angle = pickle.load(inp)
        E_lower = pickle.load(inp)
        N_upper = pickle.load(inp)
    data = (dem_data, gnss_mapping, gnss, time, points, observers, observers_cartesian, elevation_angle, E_lower, N_upper)
    for r in main(data):
        print(r)