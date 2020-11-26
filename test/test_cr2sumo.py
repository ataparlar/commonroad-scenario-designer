# -*- coding: utf-8 -*-
"""Test case file for SUMO to CR conversion and simulation"""

import os
import unittest
from parameterized import parameterized
from typing import List

import numpy as np
from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.common.file_writer import CommonRoadFileWriter
from crmapconverter.sumo_map.config import SumoConfig
from crmapconverter.sumo_map.cr2sumo import CR2SumoMapConverter
from sumocr.interface.sumo_simulation import SumoSimulation


# force test execution to be in specified order
# unittest.TestLoader.sortTestMethodsUsing = lambda _, x, y: cmp(y, x)


class BaseClass(unittest.TestCase):
    """Test the conversion from an CommonRoad map to a SUMO .net.xml file
    """
    proj_string = ""
    scenario_name = None
    cwd_path = None
    out_path = None
    scenario = None

    def read_cr_file(self, cr_file_name: str):
        """Load the osm file and convert it to a scenario."""
        if not self.scenario_name:
            self.scenario_name = cr_file_name

        self.cwd_path = os.path.dirname(os.path.abspath(__file__))
        self.out_path = os.path.join(self.cwd_path, ".pytest_cache")

        if not os.path.isdir(self.out_path):
            os.makedirs(self.out_path)
        else:
            for (dirpath, _, filenames) in os.walk(self.out_path):
                for file in filenames:
                    if file.endswith('.xml'):
                        os.remove(os.path.join(dirpath, file))

        self.path = os.path.join(self.cwd_path, "sumo_xml_test_files",
                                 cr_file_name + ".xml")

        self.scenario, planning_problem = CommonRoadFileReader(
            self.path).open()

        # translate scenario to center
        centroid = np.mean(np.concatenate([
            l.center_vertices for l in self.scenario.lanelet_network.lanelets
        ]),
            axis=0)
        self.scenario.translate_rotate(-centroid, 0)
        planning_problem.translate_rotate(-centroid, 0)
        config = SumoConfig.from_scenario_name(self.scenario_name)
        # convert to SUMO
        wrapper = CR2SumoMapConverter(self.scenario.lanelet_network, config)
        return config, wrapper

    def sumo_run(self, config: SumoConfig, wrapper: CR2SumoMapConverter, tls_lanelet_ids: List[int]):
        # was the conversion successful?
        conversion_successfull = wrapper.convert_to_net_file(
            os.path.dirname(self.path))
        self.assertTrue(conversion_successfull)

        # can we generate traffic light systems?
        if tls_lanelet_ids:
            self.assertTrue(
                all(wrapper.auto_generate_traffic_light_system(lanelet_id)
                    for lanelet_id in tls_lanelet_ids)
            )

        simulation = SumoSimulation()
        simulation.initialize(config, wrapper)

        for _ in range(config.simulation_steps):
            simulation.simulate_step()
        simulation.stop()

        simulated_scenario = simulation.commonroad_scenarios_all_time_steps()
        self.assertIsNotNone(simulated_scenario)

        # write simulated scenario to disk
        CommonRoadFileWriter(
            simulated_scenario,
            None,
            author=self.scenario.author,
            affiliation=self.scenario.affiliation,
            source=self.scenario.source,
            tags=self.scenario.tags,
            location=self.scenario.location).write_scenario_to_file(
            os.path.join(os.path.dirname(self.path),
                         self.scenario_name + ".simulated.xml"),
            overwrite_existing_file=True)
        # check validity of written file


class ParametrizedTestSequence(BaseClass):
    @parameterized.expand([
        ['USA_Peach-3_3_T-1', []],
        ["garching", [270]],
        ["intersect_and_crossing", [56]],
        ["merging_lanelets_utm", [107]],
        ["urban-1_lanelets_utm", [105]],
        ["DEU_AAH-1_8007_T-1", [154]],
        ["DEU_AAH-2_19000_T-1", [118]],
        ["DEU_Guetersloh-20_4_T-1", []],
        ["DEU_Muc-13_1_T-1", []],
        ["USA_Lanker-2_13_T-1", []]
    ])
    def test_sumo_run(self, file_name: str, tls: List[int]):
        config, wrapper = self.read_cr_file(file_name)
        self.sumo_run(config, wrapper, tls)


if __name__ == "__main__":
    unittest.main()
