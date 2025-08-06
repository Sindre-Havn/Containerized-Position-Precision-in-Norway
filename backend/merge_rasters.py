import os
from shapely import LineString, Point, box
import rasterio
from rasterio.merge import merge
import rasterio
import config
from pyproj import Transformer
import numpy as np

from time import perf_counter_ns


# First, download the elevation data from hoydedata.no for the area you want to work with.
# Nation-wide cover is recomended.
# Unzip the nation-wide .tif files and place them in folder "dtm10"


def convert_coordinates(wgs_coords: list[list[np.float64]]) -> list[list[float]]:
    """
    Convert WGS84 coordinates to UTM 33N coordinates.
    """
    coords = np.array(wgs_coords)
    transformerToEN = Transformer.from_crs("EPSG:4326","EPSG:25833", always_xy=True)
    transformed_points = np.column_stack(transformerToEN.transform(coords[:, 0], coords[:, 1]))
    return transformed_points.tolist()


def merge_rasters_near_points(points_dicts_wgs: list[dict]) -> None:
    """
    Merges all available rasterfiles with boundaries intersecting the points.
    The boundery box of the .tif files is upsized by a MARGIN constant in case
    points is close to such boundary.
    """

    points_wgs = [d['geometry']['coordinates'] for d in points_dicts_wgs]
    line_points_EN = convert_coordinates(points_wgs)
    points = LineString(line_points_EN) if len(points_dicts_wgs)>1 else Point(line_points_EN[0])

    # Find all .tif files in the folder
    FOLDER_PATH = "dtm10/"
    tif_files = [os.path.join(FOLDER_PATH, f) for f in os.listdir(FOLDER_PATH) if f.endswith(".tif")]

    covering_rasters = []

    # MARGIN is added because the horizon view from a point, may be blocked by tall terrain in a neighbouring .tif file (neighbour .tif to the points .tif).
    MARGIN = config.MARGIN_TO_NEIGHBOURING_TIF
    for file in tif_files:
        raster = rasterio.open(file)
        bounds = raster.bounds
        
        raster_bbox = box(bounds.left-MARGIN, bounds.bottom-MARGIN, bounds.right+MARGIN, bounds.top+MARGIN)

        if raster_bbox.intersects(points):
            covering_rasters.append(raster)
            # print(file)
        else:
            raster.close()

    if not covering_rasters:
        raise ValueError("No rasterfile covers the area you specified!")

    # Merge rasters
    mosaic, out_transform = merge(covering_rasters)

    # Copy data from first raster
    out_meta = covering_rasters[0].meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "height": mosaic.shape[1],
        "width": mosaic.shape[2],
        "transform": out_transform
    })

    output_path = "merged_rasters/merged_raster.tif"
    with rasterio.open(output_path, "w", **out_meta) as dest:
        dest.write(mosaic)

    # Close rasters
    for raster in covering_rasters:
        raster.close()


# Test
# createNewRaster([446098.28,7371410.12],	[475901.49, 7365141.92])