# -*- coding: utf-8 -*-


"""Module to contain Network which can load an opendrive object and then export
to lanelets. Iternally, the road network is represented by ParametricLanes."""
import copy
import enum
import warnings

import numpy as np
import inspect
from commonroad.scenario.scenario import Scenario, GeoTransformation, Location, ScenarioID
from collections import defaultdict

from crmapconverter.opendrive.opendriveparser.elements.opendrive import OpenDrive

from crmapconverter.opendrive.opendriveconversion.conversion_lanelet_network import ConversionLaneletNetwork
from crmapconverter.opendrive.opendriveconversion.converter import OpenDriveConverter
from crmapconverter.opendrive.opendriveconversion.plane_elements.traffic_signals import get_traffic_signals
from crmapconverter.opendrive.opendriveconversion.plane_elements.geo_reference import get_geo_reference
from crmapconverter.opendrive.opendriveconversion.utils import encode_road_section_lane_width_id

__author__ = "Benjamin Orthen, Stefan Urban, Sebastian Maierhofer"
__copyright__ = "TUM Cyber-Physical Systems Group"
__credits__ = ["Priority Program SPP 1835 Cooperative Interacting Automobiles"]
__version__ = "1.2.0"
__maintainer__ = "Sebastian Maierhofer"
__email__ = "commonroad-i06@in.tum.de"
__status__ = "Released"


class CountryID(enum.Enum):
    """
    Enum describing different country code as per ISO 3166-1, alpha-2 codes.
    """
    GERMANY = 'DEU'
    UNITED_STATES_OF_AMERICA = 'USA'
    CHINA = 'CNN'
    RUSSIA = 'RUS'
    SPAIN = 'ESP'
    ARGENTINA = 'ARG'
    BELGIUM = 'BEL'
    FRANCE = 'FRA'
    GREECE = 'GRE'
    CROATIA = 'HRV'
    PUERTO_RICO = 'PRI'
    OPEN_DRIVE = 'ZAM'

class Network:
    """Represents a network of parametric lanes, with a LinkIndex
    which stores the neighbor relations between the parametric lanes.

    Args:

    """

    def __init__(self):
        self._planes = []
        self._link_index = None
        self._geo_ref = None
        self._traffic_lights = []
        self._traffic_signs = []
        self._stop_lines = []
        self._country_ID = None


    # def __eq__(self, other):
    # return self.__dict__ == other.__dict__

    def load_opendrive(self, opendrive: OpenDrive):
        """Load all elements of an OpenDRIVE network to a parametric lane representation

        Args:
          opendrive:

        """

        self._link_index = LinkIndex()
        self._link_index.create_from_opendrive(opendrive)

        try:
            self._geo_ref = opendrive.header.geo_reference
        except TypeError:
            self._geo_ref = None

        # Get country ID form signal data in openDrive
        self._country_ID = OpenDriveConverter.get_country_ID(opendrive.roads)

        # Convert all parts of a road to parametric lanes (planes)
        for road in opendrive.roads:
            road.planView.precalculate()
            # The reference border is the base line for the whole road
            reference_border = OpenDriveConverter.create_reference_border(
                road.planView, road.lanes.laneOffsets
            )
            # Extracting signals, signs and stop lines from each road

            # signal_references = get_traffic_signal_references(road)
            # A lane section is the smallest part that can be converted at once
            for lane_section in road.lanes.lane_sections:
                parametric_lane_groups = OpenDriveConverter.lane_section_to_parametric_lanes(
                    lane_section, reference_border
                )

                self._planes.extend(parametric_lane_groups)

            traffic_lights, traffic_signs, stop_lines = get_traffic_signals(road)
            self._traffic_lights.extend(traffic_lights)
            self._traffic_signs.extend(traffic_signs)
            self._stop_lines.extend(stop_lines)

    def export_lanelet_network(
            self, filter_types: list = None
    ) -> "ConversionLaneletNetwork":
        """Export network as lanelet network.

        Args:
          filter_types: types of ParametricLane objects to be filtered. (Default value = None)

        Returns:
          The converted LaneletNetwork object.
        """

        # Convert groups to lanelets
        lanelet_network = ConversionLaneletNetwork()

        for parametric_lane in self._planes:

            if filter_types is not None and parametric_lane.type not in filter_types:
                self._link_index.clean_intersections(parametric_lane.id_)
                continue

            lanelet = parametric_lane.to_lanelet()
            lanelet.predecessor = self._link_index.get_predecessors(parametric_lane.id_)
            lanelet.successor = self._link_index.get_successors(parametric_lane.id_)
            lanelet_network.add_lanelet(lanelet)

            # Create a map of lanelet_description to traffic signs/lights so that they can be assigned as
            # reference to the correct lanelets later

        # prune because some
        # successorIds get encoded with a non existing successorID
        # of the lane link
        lanelet_network.prune_network()

        # concatenate possible lanelets with their successors
        replacement_id_map = lanelet_network.concatenate_possible_lanelets()
        self._link_index.concatenate_lanes_in_intersection_map(replacement_id_map)

        # Perform lane splits and joins
        lanelet_network.join_and_split_possible_lanes()

        lanelet_network.convert_all_lanelet_ids()
        self._link_index.update_intersection_lane_id(lanelet_network.old_lanelet_ids())
        # self.traffic_signal_elements.update_traffic_signs_map_lane_id(lanelet_network.old_lanelet_ids())

        # generating intersections
        intersection_id_counter = 0
        for intersection_map in self._link_index.intersection_maps():
            # Remove lanelets that are not part of the network (as they are of a different type)
            lanelet_network.create_intersection(intersection_map, intersection_id_counter)
            intersection_id_counter += 1

        # Assign traffic signals, lights and stop lines to lanelet network
        lanelet_network.add_traffic_lights_to_network(self._traffic_lights)
        lanelet_network.add_traffic_signs_to_network(self._traffic_signs)
        lanelet_network.add_stop_lines_to_network(self._stop_lines)

        return lanelet_network

    def export_commonroad_scenario(
            self, dt: float = 0.1, benchmark_id=None, filter_types=None
    ):
        """Export a full CommonRoad scenario

        Args:
          dt:  (Default value = 0.1)
          benchmark_id:  (Default value = None)
          filter_types:  (Default value = None)

        Returns:

        """
        if self._geo_ref is not None:
            longitude, latitude = get_geo_reference(self._geo_ref)
            geo_transformation = GeoTransformation(geo_reference=self._geo_ref)

            if longitude is not None and latitude is not None:
                location = Location(
                    geo_transformation=geo_transformation,
                    gps_latitude=latitude, gps_longitude=longitude
                )

            else:
                location = Location(geo_transformation=geo_transformation)
        else:
            location = None

        # TODO create default scenario ID or implement workaround in commonroad-io
        scenario_id = ScenarioID(country_id="ZAM", map_name="OpenDrive", map_id=123)

        scenario = Scenario(
            dt=dt, scenario_id=scenario_id,
            location=location
        )

        scenario.add_objects(
            self.export_lanelet_network(
                filter_types=filter_types
                if isinstance(filter_types, list)
                else ["driving", "onRamp", "offRamp", "exit", "entry"]
            )
        )

        return scenario


class LinkIndex:
    """Overall index of all links in the file, save everything as successors, predecessors can be
    found via a reverse search"""

    def __init__(self):
        self._successors = {}
        self._intersections = list()
        self._intersection_dict = dict()

    def intersection_maps(self):
        return self._intersections

    def create_from_opendrive(self, opendrive):
        """Create a LinkIndex from an OpenDrive object.

        Args:
          opendrive: OpenDrive style object.

        Returns:

        """
        self._add_junctions(opendrive)

        # Extract link information from road lanes
        for road in opendrive.roads:
            for lane_section in road.lanes.lane_sections:
                for lane in lane_section.allLanes:
                    parametric_lane_id = encode_road_section_lane_width_id(
                        road.id, lane_section.idx, lane.id, -1
                    )

                    # Not the last lane section? > Next lane section in same road
                    if lane_section.idx < road.lanes.getLastLaneSectionIdx():
                        successorId = encode_road_section_lane_width_id(
                            road.id, lane_section.idx + 1, lane.link.successorId, -1
                        )

                        self.add_link(parametric_lane_id, successorId, lane.id >= 0)

                    # Last lane section! > Next road in first lane section
                    # Try to get next road
                    elif (
                            road.link.successor is not None
                            and road.link.successor.elementType != "junction"
                    ):

                        next_road = opendrive.getRoad(road.link.successor.element_id)

                        if next_road is not None:

                            if road.link.successor.contactPoint == "start":
                                successorId = encode_road_section_lane_width_id(
                                    next_road.id, 0, lane.link.successorId, -1
                                )

                            else:  # contact point = end
                                successorId = encode_road_section_lane_width_id(
                                    next_road.id,
                                    next_road.lanes.getLastLaneSectionIdx(),
                                    lane.link.successorId,
                                    -1,
                                )
                            self.add_link(parametric_lane_id, successorId, lane.id >= 0)

                    # Not first lane section? > Previous lane section in same road
                    if lane_section.idx > 0:
                        predecessorId = encode_road_section_lane_width_id(
                            road.id, lane_section.idx - 1, lane.link.predecessorId, -1
                        )

                        self.add_link(predecessorId, parametric_lane_id, lane.id >= 0)

                    # First lane section! > Previous road
                    # Try to get previous road
                    elif (
                            road.link.predecessor is not None
                            and road.link.predecessor.elementType != "junction"
                    ):

                        prevRoad = opendrive.getRoad(road.link.predecessor.element_id)

                        if prevRoad is not None:

                            if road.link.predecessor.contactPoint == "start":
                                predecessorId = encode_road_section_lane_width_id(
                                    prevRoad.id, 0, lane.link.predecessorId, -1
                                )

                            else:  # contact point = end
                                predecessorId = encode_road_section_lane_width_id(
                                    prevRoad.id,
                                    prevRoad.lanes.getLastLaneSectionIdx(),
                                    lane.link.predecessorId,
                                    -1,
                                )
                            self.add_link(
                                predecessorId, parametric_lane_id, lane.id >= 0
                            )

    def add_intersection_link(self, parametric_lane_id, successor, reverse: bool = False):
        """
        Similar to add_link, adds successors only in an intersection
        """
        if reverse:
            self.add_intersection_link(successor, parametric_lane_id)
            return

        if parametric_lane_id not in self._intersection_dict:
            self._intersection_dict[parametric_lane_id] = []

        if successor not in self._intersection_dict[parametric_lane_id]:
            self._intersection_dict[parametric_lane_id].append(successor)

    def add_link(self, parametric_lane_id, successor, reverse: bool = False):
        """

        Args:
          parametric_lane_id:
          successor:
          reverse:  (Default value = False)

        Returns:

        """

        # if reverse, call function recursively with switched parameters
        if reverse:
            self.add_link(successor, parametric_lane_id)
            return

        if parametric_lane_id not in self._successors:
            self._successors[parametric_lane_id] = []

        if successor not in self._successors[parametric_lane_id]:
            self._successors[parametric_lane_id].append(successor)

    def _add_junctions(self, opendrive):
        """

        Args:
          opendrive:

        Returns:

        """
        # add junctions to link_index
        # if contact_point is start, and laneId from connecting_road is negative
        # the connecting_road is the successor
        # if contact_point is start, and laneId from connecting_road is positive
        # the connecting_road is the predecessor
        # for contact_point == end it's exactly the other way
        for junction in opendrive.junctions:
            for connection in junction.connections:
                incoming_road = opendrive.getRoad(connection.incomingRoad)
                connecting_road = opendrive.getRoad(connection.connectingRoad)
                contact_point = connection.contactPoint

                for lane_link in connection.laneLinks:
                    if contact_point == "start":

                        # decide which lane section to use (first or last)
                        if lane_link.fromId < 0:
                            lane_section_idx = (
                                incoming_road.lanes.getLastLaneSectionIdx()
                            )
                        else:
                            lane_section_idx = 0
                        incoming_road_id = encode_road_section_lane_width_id(
                            incoming_road.id, lane_section_idx, lane_link.fromId, -1
                        )
                        connecting_road_id = encode_road_section_lane_width_id(
                            connecting_road.id, 0, lane_link.toId, -1
                        )
                        self.add_link(
                            incoming_road_id, connecting_road_id, lane_link.toId > 0
                        )
                        self.add_intersection_link(
                            incoming_road_id, connecting_road_id, lane_link.toId > 0
                        )

                    else:
                        # decide which lane section to use (first or last)
                        if lane_link.fromId < 0:
                            lane_section_idx = 0

                        else:
                            lane_section_idx = (
                                incoming_road.lanes.getLastLaneSectionIdx()
                            )
                        incoming_road_id = encode_road_section_lane_width_id(
                            incoming_road.id, 0, lane_link.fromId, -1
                        )
                        connecting_road_id = encode_road_section_lane_width_id(
                            connecting_road.id,
                            connecting_road.lanes.getLastLaneSectionIdx(),
                            lane_link.toId,
                            -1,
                        )
                        self.add_link(
                            incoming_road_id, connecting_road_id, lane_link.toId < 0
                        )
                        self.add_intersection_link(
                            incoming_road_id, connecting_road_id, lane_link.toId < 0
                        )
            # Extracting opendrive junction links to formulate commonroad intersections
            # intersection_map = copy.copy(self._successors)
            self._intersections.append(self._intersection_dict)
            self._intersection_dict = dict()

    def remove(self, parametric_lane_id):
        """

        Args:
          parametric_lane_id:

        """
        # Delete key
        if parametric_lane_id in self._successors:
            del self._successors[parametric_lane_id]

        # Delete all occurances in successor lists
        for successorsId, successors in self._successors.items():
            if parametric_lane_id in successors:
                self._successors[successorsId].remove(parametric_lane_id)

    def get_successors(self, parametric_lane_id: str) -> list:
        """

        Args:
          parametric_lane_id: Id of ParametricLane for which to search
            successors.

        Returns:
          List of successors belonging the the ParametricLane.
        Par
        """
        if parametric_lane_id not in self._successors:
            return []

        return self._successors[parametric_lane_id]

    def get_predecessors(self, parametric_lane_id: str) -> list:
        """

        Args:
          parametric_lane_id: Id of ParametricLane for which to search predecessors.

        Returns:
          List of predecessors of a ParametricLane.
        """
        predecessors = []
        for successor_plane_id, successors in self._successors.items():
            if parametric_lane_id not in successors:
                continue

            if successor_plane_id in predecessors:
                continue

            predecessors.append(successor_plane_id)

        return predecessors

    def clean_intersections(self, parametric_lane_id):
        """
        Remove lanes that are not part of the lanelet network
        """
        for intersection in self._intersections:
            if parametric_lane_id in intersection.keys():
                del intersection[parametric_lane_id]
        return

    def concatenate_lanes_in_intersection_map(self, replacement_id_map):
        """
        Lanelets are concatenated if possible, hence some lanelets ids that exist in intersections
        are no longer valid and also need to be replaced with the lanelet id they are concatenated with.
        """
        updated_intersection_maps = []
        for intersection_map in self.intersection_maps():
            intersection_map_concatenated_lanelets = copy.copy(intersection_map)
            # Check if old lanelet is in keys
            for old_id, new_id in replacement_id_map.items():
                for incoming, successors in intersection_map.items():
                    updated_successors = [new_id if x == old_id else x for x in successors]
                    intersection_map[incoming] = updated_successors
                if old_id in intersection_map.keys():
                    intersection_map_concatenated_lanelets[new_id] = intersection_map[old_id]
                    del intersection_map_concatenated_lanelets[old_id]

                # Check if old lanelet is in values
            updated_intersection_maps.append(intersection_map_concatenated_lanelets)
        self._intersections = updated_intersection_maps

    def update_intersection_lane_id(self, old_id_to_new_id_map):
        """
        Updates the  ids in the lanelet map
        """

        updated_intersection_maps = []
        for intersection_map in self.intersection_maps():
            intersection_map_new_id = dict()
            for incoming, connecting in intersection_map.items():
                # Replacing keys/incoming ids with new ids
                # print("from", incoming, "to", old_id_to_new_id_map[incoming])
                new_incoming_id = old_id_to_new_id_map[incoming]
                connecting = [old_id_to_new_id_map.get(item) for item in connecting]
                intersection_map_new_id[new_incoming_id] = connecting

            updated_intersection_maps.append(intersection_map_new_id)
        self._intersections = updated_intersection_maps

class TrafficSignalElements:
    """
    Class containing the information regarding how traffic signs lights and references are mapped to lanelets
    """
    def __init__(self):
        self.traffic_sign_to_lanelet_mapper = defaultdict(list)
        self.traffic_light_to_lanelet_mapper = defaultdict(list)
        self.stopline_to_lanelet_mapper = defaultdict(list)
        self.signal_reference_to_lanelet_id_mapper = defaultdict(list)

    def replace_concatenated_lanes_for_traffic_signs_map(self, replacement_ids):
        """
        Replaces the lanelet id in the values of the dictionaries in order to update any lanelet
        that has been concatenated with another lanelet
        """
        for key, lanelets in self.signal_reference_to_lanelet_id_mapper.items():
            self.signal_reference_to_lanelet_id_mapper[key][:] = [replacement_ids[lane] if lane in replacement_ids.keys() else lane for lane in lanelets]
        for key, lanelets in self.stopline_to_lanelet_mapper.items():
            self.stopline_to_lanelet_mapper[key][:] = [replacement_ids[lane] if lane in replacement_ids.keys() else lane for lane in lanelets]
        for key, lanelets in self.traffic_sign_to_lanelet_mapper.items():
            self.traffic_sign_to_lanelet_mapper[key][:] = [replacement_ids[lane] if lane in replacement_ids.keys() else lane for lane in lanelets]
        for key, lanelets in self.traffic_light_to_lanelet_mapper.items():
            self.traffic_light_to_lanelet_mapper[key][:] = [replacement_ids[lane] if lane in replacement_ids.keys() else lane for lane in lanelets]

    def update_traffic_signs_map_lane_id(self, lanelet_id_map):
        """
        Updates the ids of  all the lanelets stored in the dictionaries to the newly assigned lanelet id
        """
        for key, lanelets in self.signal_reference_to_lanelet_id_mapper.items():
            self.signal_reference_to_lanelet_id_mapper[key][:] = [lanelet_id_map[lane] if lane in lanelet_id_map.keys() else lane for lane in lanelets]
        for key, lanelets in self.stopline_to_lanelet_mapper.items():
            self.stopline_to_lanelet_mapper[key][:] = [lanelet_id_map[lane] if lane in lanelet_id_map.keys() else lane for lane in lanelets]
        for key, lanelets in self.traffic_sign_to_lanelet_mapper.items():
            self.traffic_sign_to_lanelet_mapper[key][:] = [lanelet_id_map[lane] if lane in lanelet_id_map.keys() else lane for lane in lanelets]
        for key, lanelets in self.traffic_light_to_lanelet_mapper.items():
            self.traffic_light_to_lanelet_mapper[key][:] = [lanelet_id_map[lane] if lane in lanelet_id_map.keys() else lane for lane in lanelets]
