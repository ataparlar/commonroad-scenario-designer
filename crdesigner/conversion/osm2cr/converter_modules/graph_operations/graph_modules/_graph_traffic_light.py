from queue import Queue
from typing import List, Set, Tuple, Optional, Dict
from ordered_set import OrderedSet
import numpy as np
from commonroad.scenario.traffic_sign import TrafficSign, TrafficLight
from commonroad.geometry.shape import Polygon

from crdesigner.conversion.osm2cr import config
from crdesigner.conversion.osm2cr.converter_modules.utility import geometry, traffic_sign_parser, idgenerator
from crdesigner.conversion.osm2cr.converter_modules.utility.custom_types import (
    Road_info,
    Assumption_info,
)
import math

from ._graph_node import GraphNode


class GraphTrafficLight:
    def __init__(self, light: Dict,
                 node: GraphNode):
        self.light = light
        self.node = node
        self.id = idgenerator.get_id()
        self.crossing = False
        self.highway = False
        self.forward = True
        self.parse_osm(light)

    def parse_osm(self, data: Dict):
        if 'crossing' in data:
            self.crossing = True
        if 'highway' in data:
            self.highway = True
        if 'traffic_signals:direction' in data:
            if data['traffic_signals:direction'] == 'backward':
                self.forward = False

    def to_traffic_light_cr(self):
        position = None
        if self.node is not None:
            position_point = self.node.get_point()
            position = np.array([position_point.x, position_point.y])
        traffic_light = TrafficLight(self.id, cycle=[], position=position)
        return traffic_light