# concurrency.py / app.py
USE_CONCURRENCY_FOR_DOPVALUES = True
PROCESSES_COUNT_DOPVALUES = 7

USE_CONCURRENCY_FOR_SATELLITE = True
PROCESSES_COUNT_SATELLITE = 7

# romsadalenRoad.py
USE_CORRECT_SPEEDLIMITS = True # Does a GET request for the speedlimit for every parial roadsegment in route. Is 'correct' but slow and expensive.
DEFAULT_SPEEDLIMIT = 50 # km/h, used in absence of defined speedlimit.
HEADERS = {
            "Accept": "application/json",
            "X-Client": "Masteroppgave-vegnett"
}

# generateElevationMask.py / computebaner.py
SKYPLOT_RESOLUTION_DEGREE = 1.0 # [float] degree.
FIND_ELEVATION_STEPSIZE = 5   # meter, how frequent along the ground plane the elevation is checked.

# download høydedata
MARGIN_TO_NEIGHBOURING_TIF = 10_000 # meters. ≈ 1750/tan(10°). From a observation point, a mountain in a neighbouring .tif grid, may obstruct line of sight to satellites. 10_000 meter is equivalent to a maximum of 1750m tall obstruction in the horizon at 10° mask angle.

# memory_manager.py / app.py
EPHEMERIS_MAX_COUNT = 4 # 50
EPHEMERIS_LIFETIME_HOURS = -1 # Negative hours are ignored -> infinite lifetime.

MERGED_RASTER_MAX_COUNT = 3 # 20
MERGED_RASTER_LIFETIME_HOURS = 0.5  # Negative hours are ignored -> infinite lifetime.