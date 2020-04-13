"""
This module holds all parameters necessary for the conversion
"""

# Benchmark settings
# name of the benchmark
import enum

BENCHMARK_ID = "test_bench"
# author of the benchmark
AUTHOR = "Automated converter by Maximilian Rieger"
# affiliation of the benchmark
AFFILIATION = "Technical University of Munich, Germany"
# source of the benchmark
SOURCE = "OpenStreetMaps (OSM)"
# additional tags for the benchmark
TAGS = "urban"
# GeonameID
GEONAME_ID = -999
# GPS latitude
GPS_LATITUDE = "123.45"
# GPS longitude
GPS_LONGITUDE = "123.45"
# time step size for the benchmark in seconds
TIMESTEPSIZE = 0.1

# Aerial Image Settings
# Use aerial images for edit
AERIAL_IMAGES = False
# Path to save downloaded aerial images
IMAGE_SAVE_PATH = "files/imagery/"
# The zoom level of Bing Maps tiles
ZOOM_LEVEL = 19
# The key to access bing maps
BING_MAPS_KEY = ""

# Map download Settings
# path to save downloaded files
SAVE_PATH = "files/"
# half width of area downloaded in meters
DOWNLOAD_EDGE_LENGTH = 200
# coordinates in latitude and longitude specifying the center of the downloaded area
DOWNLOAD_COORDINATES = (48.262447, 11.657881)

# Scenario Settings
# include tunnels in result
LOAD_TUNNELS = False
# delete unconnected edges
MAKE_CONTIGUOUS = False
# split edges at corners (~90° between two waypoint segments)
# this can help to model the course of roads on parking lots better
SPLIT_AT_CORNER = True
# use OSM restrictions for linking process
USE_RESTRICTIONS = True
# types of roads extracted from the OSM file
# suitable types: 'motorway', 'trunk', 'primary', 'secondary', 'tertiary', 'unclassified', 'residential',
# 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link', 'tertiary_link', 'living_street', 'service'
ACCEPTED_HIGHWAYS = [
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "motorway_link",
    "trunk_link",
    "primary_link",
    "secondary_link",
    "tertiary_link",
    "living_street",
    "service",
]
# number of lanes for each type of road should be >=1
LANECOUNTS = {
    "motorway": 6,
    "trunk": 4,
    "primary": 2,
    "secondary": 2,
    "tertiary": 2,
    "unclassified": 2,
    "residential": 2,
    "motorway_link": 2,
    "trunk_link": 2,
    "primary_link": 2,
    "secondary_link": 2,
    "tertiary_link": 2,
    "living_street": 2,
    "service": 2,
}
# width of lanes for each type of road in meters
LANEWIDTHS = {
    "motorway": 2.5,
    "trunk": 2.5,
    "primary": 2.5,
    "secondary": 2.5,
    "tertiary": 2.5,
    "unclassified": 2.5,
    "residential": 2.5,
    "motorway_link": 2.5,
    "trunk_link": 2.5,
    "primary_link": 2.5,
    "secondary_link": 2.5,
    "tertiary_link": 2.5,
    "living_street": 2.5,
    "service": 2.5,
}
# default speed limit for each type of road in km/h
SPEED_LIMITS = {
    "motorway": 120,
    "trunk": 100,
    "primary": 100,
    "secondary": 100,
    "tertiary": 100,
    "unclassified": 80,
    "residential": 50,
    "motorway_link": 80,
    "trunk_link": 80,
    "primary_link": 80,
    "secondary_link": 80,
    "tertiary_link": 80,
    "living_street": 7,
    "service": 10,
}

# Export Settings
# desired distance between interpolated waypoints in meters
INTERPOLATION_DISTANCE = 0.5
# allowed inaccuracy of exported lines to reduce number of way points in meters
COMPRESSION_THRESHOLD = 0.05
# export the scenario in UTM coordinates
EXPORT_IN_UTM = True
# toggle filtering of negligible waypoints
FILTER = True

# Internal settings (these can be used to improve the conversion process for individual scenarios)
# radius of the earth used for calculation in meters
EARTH_RADIUS = 6371000
# delete short edges after cropping
DELETE_SHORT_EDGES = False
# distance between waypoints used internally in meters
INTERPOLATION_DISTANCE_INTERNAL = 0.25
# bezier parameter for interpolation (should be within [0, 0.5])
BEZIER_PARAMETER = 0.35
# distance between roads at intersection used for cropping in meters
INTERSECTION_DISTANCE = 5.0
# defines if the distance to other roads is used for cropping
# if false the distance to the center of the intersection is used
INTERSECTION_CROPPING_WITH_RESPECT_TO_ROADS = True
# threshold above which angles are considered as soft in degrees
SOFT_ANGLE_THRESHOLD = 55.0
# least angle for lane segment to be added to the graph in degrees.
# if you edit the graph by hand, a value of 0 is recommended
LANE_SEGMENT_ANGLE = 5.0
# least distance between graph nodes to try clustering in meters
CLUSTER_LENGTH = 10.0
# least length of cluster to be added in meters
LEAST_CLUSTER_LENGTH = 10.0
# maximal distance between two intersections to which they are merged, if zero, no intersections are merged
MERGE_DISTANCE = 3.5

# Toggle edit for user
USER_EDIT = False

# set of processed turn lanes
# this should only be changed for further development
RECOGNIZED_TURNLANES = [
    "left",
    "through",
    "right",
    "merge_to_left",
    "merge_to_right",
    "through;right",
    "left;through",
    "left;through;right",
    "left;right",
    "none",
]

TRAFFIC_SIGN_VALUES = [
    "traffic_signals",
    "stop",
    "give_way",
    "city_limit",
]
TRAFFIC_SIGN_KEYS = [
    "traffic_sign",
    "overtaking",
    "traffic_signals:direction",
    "maxspeed",
]


@enum.unique
class TrafficSignID(enum.Enum):
    MAXSPEED = '274'
    OVERTAKING = '276'
    CITYLIMIT = '310'
    GIVEWAY = '205'
    STOP = '206'
    UNKNOWN = ''


TRAFFIC_SIGN_MAP = {
    'maxspeed': TrafficSignID.MAXSPEED,
    'overtaking': TrafficSignID.OVERTAKING,
    'city_limit': TrafficSignID.CITYLIMIT,
    'give_way': TrafficSignID.GIVEWAY,
    'stop': TrafficSignID.STOP,
}
