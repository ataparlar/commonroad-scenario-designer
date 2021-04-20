import os
import matplotlib.pyplot as plt
import numpy as np
from lxml import etree
import uuid

from commonroad.common.file_reader import CommonRoadFileReader
from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile
from commonroad.visualization.draw_dispatch_cr import draw_object

from crdesigner.io.api import commonroad_to_sumo

from crdesigner.io.gui.toolboxes.gui_sumo_simulation import SUMO_AVAILABLE
if SUMO_AVAILABLE:
    from crdesigner.conversion.sumo_map.config import SumoConfig
    from crdesigner.conversion.sumo_map.cr2sumo import CR2SumoMapConverter
    from sumocr.interface.sumo_simulation import SumoSimulation
    from sumocr.visualization.video import create_video


output_folder = ""  # replace empty string
scenario_name = ""  # replace empty string
input_file = os.path.join(output_folder, scenario_name + '.xml')

scenario, planning_problem = CommonRoadFileReader(input_file).open()

# ----------------------------------------------- Option 1: General API ------------------------------------------------
commonroad_to_sumo(input_file, output_folder)

# ------------------------------------------ Option 2: SUMO conversion APIs --------------------------------------------
try:
    commonroad_reader = CommonRoadFileReader(input_file)
    scenario, _ = commonroad_reader.open()
except etree.XMLSyntaxError as xml_error:
    print(f"SyntaxError: {xml_error}")
    print(
        "There was an error during the loading of the selected CommonRoad file.\n")

if SUMO_AVAILABLE:
    config = SumoConfig.from_scenario_name(str(uuid.uuid4()))
    config.scenario_name = scenario_name
    converter = CR2SumoMapConverter(scenario.lanelet_network, config)
    converter.convert_to_net_file(output_folder)

# -------------------- Option 3: SUMO conversion APIs with Traffic Simulation and Video Creation -----------------------

# translate scenario to center
centroid = np.mean(np.concatenate(
    [la.center_vertices for la in scenario.lanelet_network.lanelets]),
    axis=0)
scenario.translate_rotate(-centroid, 0)
planning_problem.translate_rotate(-centroid, 0)

config = SumoConfig.from_scenario_name(scenario_name)

# convert CR to sumo net
wrapper = CR2SumoMapConverter(scenario.lanelet_network, config)
wrapper.convert_to_net_file(output_folder)
tls_lanelet_id = 43513
traffic_light_system_generated = wrapper.auto_generate_traffic_light_system(tls_lanelet_id)

print(f"Generated Traffic Light System at {tls_lanelet_id}, {traffic_light_system_generated}")

# draw scenario after traffic light generation
plt.figure(figsize=(25, 25))
draw_object(wrapper.lanelet_network)
plt.axis('equal')
plt.autoscale()
plt.show()

# write generated traffic lights back to commonroad file
scenario.lanelet_network = wrapper.lanelet_network

# run Simulation
simulation = SumoSimulation()
simulation.initialize(config, wrapper)

for t in range(config.simulation_steps):
    simulation.simulate_step()

simulation.stop()

# save resulting scenario
simulated_scenario = simulation.commonroad_scenarios_all_time_steps()
CommonRoadFileWriter(simulated_scenario,
                     planning_problem,
                     author=scenario.author,
                     affiliation=scenario.affiliation,
                     source=scenario.source,
                     tags=scenario.tags,
                     location=scenario.location).write_scenario_to_file(
    os.path.join(output_folder,
                 config.scenario_name + ".simulated.xml"),
    overwrite_existing_file=OverwriteExistingFile.ALWAYS)

print("creating video (this may take some time)")
create_video(simulation, 1, config.simulation_steps, output_folder)