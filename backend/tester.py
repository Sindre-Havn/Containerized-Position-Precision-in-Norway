import json
from flask import Flask, Response, jsonify, request, stream_with_context
from computebaner import  get_gnss, getDayNumber, runData
from computeDOP import best, find_dop_along_road, find_dop_on_point
from flask_cors import CORS
from datetime import datetime, time
from romsdalenRoad import calculate_travel_time, get_road_api
import rasterio
import numpy as np

latlng = (7.68860611,62.55786489)
test = runData(['GPS','Galileo'], '10', '2025-03-25T12:00:00.000', 0, latlng)
print(test[1])