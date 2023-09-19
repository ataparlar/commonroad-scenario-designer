from commonroad.scenario.traffic_sign import TrafficSignIDGermany, TrafficSignIDZamunda, TrafficSignIDUsa

from crdesigner.config.config_base import BaseConfig, Attribute
from crdesigner.config.gui_config import gui_config


class Lanelet2Config(BaseConfig):
    """
    Lanelet2Config contains all the configuration parameters for the conversion from lanelet2 to CommonRoad.
    """
    # cr2lanelet
    ways_are_equal_tolerance = Attribute(0.001, "Ways are equal tolerance",
                                         "Value of the tolerance for which we mark ways as equal")

    autoware = Attribute(False, "Autoware", "Boolean indicating whether the conversion should be autoware compatible")

    use_local_coordinates = Attribute(False, "Use local coordinates",
                                      "Boolean indicating whether local coordinates should be added")

    supported_countries = Attribute([TrafficSignIDGermany, TrafficSignIDZamunda, TrafficSignIDUsa],
                                    "Supported countries", "Supported countries for traffic sign cr2lanelet conversion")

    supported_countries_prefixes = Attribute(
            {"TrafficSignIDZamunda": "de", "TrafficSignIDGermany": "de", "TrafficSignIDUsa": "us"},
            "Supported countries prefixes",
            "Prefix dictionary for supported countries for traffic sign cr2lanelet conversion")

    supported_lanelet2_subtypes = Attribute(
            ["urban", "country", "highway", "busLane", "bicycleLane", "exitRamp", "sidewalk", "crosswalk"],
            "Supported lanelet2 subtypes", "Lanelet2 subtypes that are available in commonroad")

    # lanelet2cr
    node_distance_tolerance = Attribute(0.01, "Node distance tolerance",
                                        "Value of the tolerance (in meters) for which we mark nodes as equal")

    priority_signs = Attribute(["PRIORITY", "RIGHT_OF_WAY"], "Priority signs", "List of priority signs")

    adjacent_way_distance_tolerance = Attribute(0.05, "Adjacent way distance tolerance",
                                                "Threshold indicating adjacent way")

    start_node_id_value = Attribute(10, "Start Node ID", "Initial node ID")

    left_driving = Attribute(False, "Left Driving", "Map describes left driving system")

    adjacencies = Attribute(True, "Adjacencies",
                            "Detect left and right adjacencies of lanelets if they do not share a common way")

    proj_string = Attribute(gui_config.pseudo_mercator, "Projection string",
                            "String used for the initialization of projection")

    translate = Attribute(False, "Translate",
                          "Boolean indicating whether map should be translated by the location coordinate specified "
                          "in the CommonRoad map")

    allowed_tags = Attribute(["type", "subtype", "one_way", "virtual", "location", "bicycle", 'highway'],
                             "Allowed Tags", "Lanelet tags which are considered for conversion. "
                                             "Lanelets with other tags are not converted.")

    LAYOUT = [["CommonRoad To Lanelet2", ways_are_equal_tolerance, autoware,
               use_local_coordinates, supported_countries, supported_countries_prefixes, supported_lanelet2_subtypes,
               "General", proj_string, translate, left_driving],
              ["Lanelet2 To CommonRoad", node_distance_tolerance, adjacent_way_distance_tolerance, start_node_id_value,
               priority_signs, adjacencies, allowed_tags]]


lanelet2_config = Lanelet2Config()