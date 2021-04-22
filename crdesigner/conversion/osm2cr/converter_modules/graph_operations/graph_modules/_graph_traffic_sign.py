
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




class GraphTrafficSign:
    def __init__(self, sign: Dict,
                 node: GraphNode = None, edges: List = [], direction: float = None):
        self.sign = sign
        self.node = node
        self.edges = edges
        self.direction = direction
        self.id = idgenerator.get_id()
       
    def to_traffic_sign_cr(self):
    
        elements = []
        position = None

        # get position
        if self.node is not None:
            position = self.node.get_cooridnates()

        # parse sign values
        tsp = traffic_sign_parser.TrafficSignParser(self.sign)
        # osm maxspeed
        if 'maxspeed' in self.sign:
            osm_maxspeed = tsp.parse_maxspeed()
            if osm_maxspeed is not None:
                elements.append(osm_maxspeed)
        # mapillary sign
        elif 'mapillary' in self.sign:
            mapillary_sign = tsp.parse_mapillary()
            if mapillary_sign is not None:
                elements.append(mapillary_sign)
        # osm traffic sign
        elif 'traffic_sign' in self.sign:
            osm_signs = tsp.parse_traffic_sign()
            if osm_signs is not None:
                elements.extend(osm_signs)

        virtual = False
        if 'virtual' in self.sign:
            if not self.sign['virtual']:
                virtual = False
            else:
                virtual = self.sign['virtual']

        first_occurrence = set()
        return TrafficSign(
            traffic_sign_id=self.id,
            traffic_sign_elements=elements,
            first_occurrence=first_occurrence,
            position=position,
            virtual=virtual)