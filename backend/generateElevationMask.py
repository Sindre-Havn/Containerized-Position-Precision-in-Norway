import numpy as np
import config


def azimuth_to_unit_circle(azimuth: float) -> float:
    """
    Transforms azimuth to unit circle angle. Output has zero degrees to the right and increase counter-clockwise.
    """
    return (90 - azimuth) % 360


def satellite_is_in_sight(observer: np.ndarray[float],
                          dem_data: np.ndarray[float],
                          E_lower: float,
                          N_upper: float,
                          elevation_satellite: float,
                          elevation_mask: float,
                          azimuth_satellite: float
                          ) -> bool:
    """
    Checks if the LOS (line of sight) from the observer to the satelitte is blocked by the terrain.
    Uses the elevation_mask and height-difference to calculate how far away it 'cares' to analyze the terrain.
    """
    if elevation_mask > elevation_satellite:
        return False

    max_dist = int((dem_data.max() -observer[2]) / np.tan(np.deg2rad(elevation_mask)))

    x,y = observer[0], observer[1]
    az = np.deg2rad(azimuth_to_unit_circle(azimuth_satellite))
    step_size = config.FIND_ELEVATION_STEPSIZE
    
    for dist in range(step_size, max_dist+step_size, step_size):
        x += step_size * np.cos(az)
        y += step_size * np.sin(az)
        try:
            row = int((N_upper-y)/10)
            col = int((x-E_lower)/10)
            
            height = dem_data[row, col]

            elevation_at_step = np.rad2deg(np.arctan((height - observer[2]) / dist))
            if elevation_at_step > elevation_satellite:
                return False
        except IndexError:
            break
    
    return True


def elevation_of_horizon(observer: np.ndarray[float],
                        dem_data: np.ndarray[float],
                        E_lower: float,
                        N_upper: float,
                        elevation_mask: float,
                        azimuth_satellite: float
                        ) -> float:
    """
    Returns the elevation (in degrees) to the horizon of the terrain, in the direction of the azimuth to a satellite.
    Uses the elevation_mask and height-difference to calculate how far away it 'cares' to analyze the terrain.
    """
    max_dist = int((dem_data.max() - observer[2]) / np.tan(np.deg2rad(elevation_mask)))

    x,y = observer[0], observer[1]
    az = np.deg2rad(azimuth_to_unit_circle(azimuth_satellite))
    max_elevation = 0
    step_size = config.FIND_ELEVATION_STEPSIZE
    
    for dist in range(step_size, max_dist+step_size, step_size):
        x += step_size * np.cos(az)
        y += step_size * np.sin(az)
        try:
            row = int((N_upper-y)/10)
            col = int((x-E_lower)/10)
            height = dem_data[row, col]

            elevation_at_step = np.rad2deg(np.arctan((height - observer[2]) / dist))
            if elevation_at_step > max_elevation:
                max_elevation = elevation_at_step

        except IndexError:
            break
    
    if max_elevation > elevation_mask:
        return max_elevation
    else:
        return elevation_mask
