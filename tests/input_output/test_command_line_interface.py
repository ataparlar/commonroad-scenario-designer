import unittest
import subprocess
from pathlib import Path
import time
import os


class TestCommandLineInterface(unittest.TestCase):
    def setUp(self) -> None:
        self.output_path = os.path.dirname(os.path.realpath(__file__)) + "/.pytest_cache"
        if not os.path.isdir(self.output_path):
            os.makedirs(self.output_path)

    def test_opendrive(self):
        subprocess.Popen(['crdesigner',
                          '--input-file', os.path.dirname(os.path.realpath(__file__))
                          + '/../map_conversion/test_maps/opendrive/poly3_and_border_record.xodr',
                          '--output-file', self.output_path + "/opendrive_command_line.xml",
                          '--tags', 'urban',
                          '--tags', 'highway',
                          'odrcr'])
        time.sleep(10)
        exists = Path(self.output_path + "/opendrive_command_line.xml")
        self.assertTrue(exists.is_file())
        exists.unlink()

    def test_osm(self):
        subprocess.Popen(['crdesigner',
                          '--input-file', os.path.dirname(os.path.realpath(__file__)) +
                          '/../map_conversion/test_maps/osm/munich.osm',
                          '--output-file', self.output_path + "/osm_command_line.xml",
                          "osmcr"])
        time.sleep(30)
        exists = Path(self.output_path + '/osm_command_line.xml')
        self.assertTrue(exists.is_file())
        exists.unlink()

    def test_lanelet2_to_cr(self):
        subprocess.Popen(['crdesigner',
                          '--input-file', os.path.dirname(os.path.realpath(__file__))
                          + '/../map_conversion/test_maps/lanelet2/traffic_priority_lanelets_utm.osm',
                          '--output-file', self.output_path + "/lanelet2_command_line.xml",
                          "lanelet2cr"])
        time.sleep(5)
        exists = Path(self.output_path + "/lanelet2_command_line.xml")
        self.assertTrue(exists.is_file())
        exists.unlink()

    def test_cr_to_lanelet(self):
        subprocess.Popen(['crdesigner',
                          '--input-file', os.path.dirname(os.path.realpath(__file__))
                          + '/../map_conversion/test_maps/lanelet2/merging_lanelets_utm.xml',
                          '--output-file', self.output_path + "/cr_lanelet_command_line.osm",
                          'crlanelet2'])
        time.sleep(5)
        exists = Path(self.output_path + "/cr_lanelet_command_line.osm")
        self.assertTrue(exists.is_file())
        exists.unlink()

    # def test_cr_to_sumo(self):
    #     if not os.path.isdir(self.output_path + '/cr_sumo_command_line'):
    #         os.makedirs(self.output_path + '/cr_sumo_command_line')
    #     subprocess.Popen(['crdesigner', 'map-convert-sumo',
    #                       '-i', os.path.dirname(os.path.realpath(__file__))
    #                       + '/../map_conversion/test_maps/sumo/ARG_Carcarana-10_2_T-1.xml',
    #                       '-o', self.output_path + "/cr_sumo_command_line" +
    #                       "/cr_sumo_command_line.net.xml", '--source_commonroad'])
    #     time.sleep(10)
    #     exists = Path(self.output_path + "/cr_sumo_command_line" + "/cr_sumo_command_line.net.xml")
    #     self.assertTrue(exists.is_file())

    def test_gui(self):
        process = subprocess.Popen(['crdesigner'])
        time.sleep(5)
        process.terminate()
        process = subprocess.Popen(['crdesigner', 'gui'])
        time.sleep(5)
        process.terminate()

    def test_map_ver_scenario(self):
        path = Path(__file__).parent.parent / "map_verification/test_maps/paper_test_maps/DEU_Guetersloh-20_1_T-1.xml"
        path_repaired = path.parent / "DEU_Guetersloh-20_1_T-1-repaired.xml"
        process = subprocess.Popen(['crdesigner',
                                    '--input-file', str(path),
                                   'verify-map'])
        time.sleep(15)
        process.terminate()
        self.assertTrue(path_repaired.exists())
        path_repaired.unlink()

    def test_map_ver_dir(self):
        path = Path(__file__).parent.parent / "map_verification/test_maps/paper_test_maps"
        path_1 = path / "DEU_Guetersloh-20_1_T-1-repaired.xml"
        path_2 = path / "DEU_BadEssen-3_1_T-1-repaired.xml"
        path_3 = path / "DEU_Reutlingen-1_1_T-1-repaired.xml"
        process = subprocess.Popen(
                ['crdesigner',
                 '--input-file', str(path),
                 'verify-dir'])
        time.sleep(30)
        process.terminate()
        self.assertTrue(path_1.exists())
        self.assertTrue(path_2.exists())
        self.assertTrue(path_3.exists())

        path_1.unlink()
        path_2.unlink()
        path_3.unlink()
