# Concurrency.py
USE_CONCURRENCY_FOR_DOPVALUES = True
PROCESSES_COUNT_DOPVALUES = 7

USE_CONCURRENCY_FOR_SATELLITE = True
PROCESSES_COUNT_SATELLITE = 7

#romsadalenRoad.py
USE_CORRECT_SPEEDLIMITS = True # Does a GET request for the speedlimit for every parial roadsegment in route. Is 'correct' but slow and expensive.
DEFAULT_SPEEDLIMIT = 50 # km/h, used in absence of defined speedlimit

HEADERS = {
            "Accept": "application/json",
            "X-Client": "Masteroppgave-vegnett"
}
