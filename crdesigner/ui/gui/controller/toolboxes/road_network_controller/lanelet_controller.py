from crdesigner.ui.gui.utilities.map_creator import MapCreator
from crdesigner.ui.gui.view.toolboxes.road_network_toolbox.lanelet_ui import AddLaneletUI
from crdesigner.ui.gui.model.scenario_model import ScenarioModel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import math


from commonroad.scenario.lanelet import LineMarking, LaneletType, RoadUser, StopLine, Lanelet
from commonroad.scenario.intersection import IncomingGroup, Intersection
from commonroad.scenario.scenario import Scenario
from commonroad.scenario.traffic_sign import *

from crdesigner.ui.gui.view.toolboxes.road_network_toolbox.road_network_toolbox_ui.road_network_toolbox_ui import \
    RoadNetworkToolboxUI


class AddLaneletController:

    def __init__(self, road_network_controller, scenario_model: ScenarioModel,
                 road_network_toolbox_ui: RoadNetworkToolboxUI):
        self.scenario_model = scenario_model
        self.road_network_toolbox_ui = road_network_toolbox_ui
        self.road_network_controller = road_network_controller
        self.lanelet_ui = AddLaneletUI(self.scenario_model, self.road_network_toolbox_ui)

    def lanelet_selection_changed(self):
        selected_lanelet = self.selected_lanelet()
        if selected_lanelet is not None:
            self.road_network_controller.selection_changed_callback(sel_lanelets=selected_lanelet)
            self.lanelet_ui.update_lanelet_information(selected_lanelet)

    def connect_gui_lanelet(self):

        self.road_network_toolbox_ui.button_add_lanelet.clicked.connect(lambda: self.add_lanelet())
        self.road_network_toolbox_ui.button_update_lanelet.clicked.connect(lambda: self.update_lanelet())
        self.road_network_toolbox_ui.selected_lanelet_update.currentIndexChanged.connect(
                lambda: self.lanelet_selection_changed())

        # Lanelet buttons
        self.road_network_toolbox_ui.button_remove_lanelet.clicked.connect(lambda: self.remove_lanelet())
        self.road_network_toolbox_ui.button_attach_to_other_lanelet.clicked.connect(
                lambda: self.attach_to_other_lanelet())

        # connect radiobuttons for adding to the adjust_add_sections function which shows and hides choices
        self.road_network_toolbox_ui.place_at_position.clicked.connect(
                lambda: self.road_network_toolbox_ui.adjust_add_sections())
        self.road_network_toolbox_ui.connect_to_previous_selection.clicked.connect(
                lambda: self.road_network_toolbox_ui.adjust_add_sections())
        self.road_network_toolbox_ui.connect_to_predecessors_selection.clicked.connect(
                lambda: self.road_network_toolbox_ui.adjust_add_sections())
        self.road_network_toolbox_ui.connect_to_successors_selection.clicked.connect(
                lambda: self.road_network_toolbox_ui.adjust_add_sections())
        self.road_network_toolbox_ui.connecting_radio_button_group.buttonClicked.connect(
                lambda: self.lanelet_ui.initialize_basic_lanelet_information(
                        self.road_network_controller.last_added_lanelet_id))

        self.road_network_toolbox_ui.button_create_adjacent.clicked.connect(lambda: self.create_adjacent())
        self.road_network_toolbox_ui.button_connect_lanelets.clicked.connect(lambda: self.connect_lanelets())
        self.road_network_toolbox_ui.button_rotate_lanelet.clicked.connect(lambda: self.rotate_lanelet())
        self.road_network_toolbox_ui.button_translate_lanelet.clicked.connect(lambda: self.translate_lanelet())
        self.road_network_toolbox_ui.button_merge_lanelets.clicked.connect(lambda: self.merge_with_successor())

    def add_lanelet(self, lanelet_id: int = None, left_vertices: np.array = None, right_vertices: np.array = None):
        """
               Adds a lanelet to the scenario based on the selected parameters by the user.

               @param lanelet_id: Id which the new lanelet should have.
               @param update: Boolean indicating whether lanelet is updated or newly created.
               @param left_vertices: Left boundary of lanelet which should be updated.
               @param right_vertices: Right boundary of lanelet which should be updated.
               """
        if not self.scenario_model.scenario_created() :
            self.road_network_controller.text_browser.append("Please create first a new scenario.")
            return

        if not self.road_network_toolbox_ui.place_at_position.isChecked() and not \
                self.road_network_toolbox_ui.connect_to_previous_selection.isChecked() and not \
                self.road_network_toolbox_ui.connect_to_successors_selection.isChecked() and not \
                self.road_network_toolbox_ui.connect_to_predecessors_selection.isChecked():
            self.road_network_controller.text_browser.append("Please select an adding option.")
            return

        predecessors = [int(pre) for pre in self.road_network_toolbox_ui.predecessors.get_checked_items()]
        successors = [int(suc) for suc in self.road_network_toolbox_ui.successors.get_checked_items()]

        place_at_position = self.road_network_toolbox_ui.place_at_position.isChecked()
        connect_to_last_selection = self.road_network_toolbox_ui.connect_to_previous_selection.isChecked()
        connect_to_predecessors_selection = self.road_network_toolbox_ui.connect_to_predecessors_selection.isChecked()
        connect_to_successors_selection = self.road_network_toolbox_ui.connect_to_successors_selection.isChecked()

        if connect_to_last_selection and self.road_network_controller.last_added_lanelet_id is None:
            self.road_network_controller.text_browser.append("__Warning__: Previously add lanelet does not exist anymore. "
                                     "Change lanelet adding option.")
            return
        if connect_to_predecessors_selection and len(predecessors) == 0:
            self.road_network_controller.text_browser.append("__Warning__: No predecessors are selected.")
            return
        if connect_to_successors_selection and len(successors) == 0:
            self.road_network_controller.text_browser.append("__Warning__: No successors are selected.")
            return

        lanelet_start_pos_x = self.get_x_position_lanelet_start(False)
        lanelet_start_pos_y = self.get_y_position_lanelet_start(False)

        lanelet_width = self.road_network_controller.get_float(self.road_network_toolbox_ui.lanelet_width)
        line_marking_left = LineMarking(self.road_network_toolbox_ui.line_marking_left.currentText())
        line_marking_right = LineMarking(self.road_network_toolbox_ui.line_marking_right.currentText())
        num_vertices = int(self.road_network_toolbox_ui.number_vertices.text())
        adjacent_left = int(
                self.road_network_toolbox_ui.adjacent_left.currentText()) if \
            self.road_network_toolbox_ui.adjacent_left.currentText() != "None" else None
        adjacent_right = int(
                self.road_network_toolbox_ui.adjacent_right.currentText()) if \
            self.road_network_toolbox_ui.adjacent_right.currentText() != "None" else None
        adjacent_left_same_direction = self.road_network_toolbox_ui.adjacent_left_same_direction.isChecked()
        adjacent_right_same_direction = self.road_network_toolbox_ui.adjacent_right_same_direction.isChecked()
        lanelet_type = {LaneletType(ty) for ty in self.road_network_toolbox_ui.lanelet_type.get_checked_items() if
                        ty != "None"}
        user_one_way = {RoadUser(user) for user in self.road_network_toolbox_ui.road_user_oneway.get_checked_items() if
                        user != "None"}
        user_bidirectional = {RoadUser(user) for user in
                              self.road_network_toolbox_ui.road_user_bidirectional.get_checked_items() if
                              user != "None"}

        traffic_signs = {int(sign) for sign in
                         self.road_network_toolbox_ui.lanelet_referenced_traffic_sign_ids.get_checked_items()}
        traffic_lights = {int(light) for light in
                          self.road_network_toolbox_ui.lanelet_referenced_traffic_light_ids.get_checked_items()}
        if self.road_network_toolbox_ui.stop_line_check_box.isChecked():
            if self.road_network_toolbox_ui.stop_line_beginning.isChecked():
                stop_line_at_end = False
                stop_line_at_beginning = True
                stop_line_marking = LineMarking(self.road_network_toolbox_ui.line_marking_stop_line.currentText())
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
            elif self.road_network_toolbox_ui.stop_line_end.isChecked():
                stop_line_at_end = True
                stop_line_at_beginning = False
                stop_line_marking = LineMarking(self.road_network_toolbox_ui.line_marking_stop_line.currentText())
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
        else:
            stop_line_at_end = False
            stop_line_at_beginning = False
            stop_line = None

        lanelet_length = self.road_network_controller.get_float(self.road_network_toolbox_ui.lanelet_length)
        lanelet_radius = self.road_network_controller.get_float(self.road_network_toolbox_ui.lanelet_radius)
        lanelet_angle = np.deg2rad(self.road_network_controller.get_float(self.road_network_toolbox_ui.lanelet_angle))
        add_curved_selection = self.road_network_toolbox_ui.curved_check_button.button.isChecked()

        if lanelet_id is None:
            lanelet_id = self.scenario_model.generate_object_id()
        if add_curved_selection:
            lanelet = MapCreator.create_curve(lanelet_width, lanelet_radius, lanelet_angle, num_vertices, lanelet_id,
                                              lanelet_type, predecessors, successors, adjacent_left, adjacent_right,
                                              adjacent_left_same_direction, adjacent_right_same_direction, user_one_way,
                                              user_bidirectional, line_marking_left, line_marking_right, stop_line,
                                              traffic_signs, traffic_lights, stop_line_at_end, stop_line_at_beginning)
        else:
            lanelet = MapCreator.create_straight(lanelet_width, lanelet_length, num_vertices, lanelet_id, lanelet_type,
                                                 predecessors, successors, adjacent_left, adjacent_right,
                                                 adjacent_left_same_direction, adjacent_right_same_direction,
                                                 user_one_way, user_bidirectional, line_marking_left,
                                                 line_marking_right, stop_line, traffic_signs, traffic_lights,
                                                 stop_line_at_end, stop_line_at_beginning)

        if connect_to_last_selection:
            last_lanelet = self.scenario_model.find_lanelet_by_id(self.road_network_controller.last_added_lanelet_id)
            lanelet.translate_rotate(np.array([last_lanelet.center_vertices[-1][0],
                                               last_lanelet.center_vertices[-1][1]]),0)
            MapCreator.fit_to_predecessor(last_lanelet, lanelet)
        elif connect_to_predecessors_selection:
            if len(predecessors) > 0:
                predecessor = self.scenario_model.find_lanelet_by_id(predecessors[0])
                lanelet.translate_rotate(np.array([predecessor.center_vertices[-1][0],
                                                   predecessor.center_vertices[-1][1]]),0)
                MapCreator.fit_to_predecessor(predecessor, lanelet)
        elif connect_to_successors_selection:
            if len(successors) > 0:
                successor = self.scenario_model.find_lanelet_by_id(successors[0])

                x_start = successor.center_vertices[0][0] - lanelet_length
                y_start = successor.center_vertices[0][1]

                lanelet.translate_rotate(np.array([x_start, y_start]), 0)
                MapCreator.fit_to_successor(successor, lanelet)
        elif place_at_position:
            lanelet.translate_rotate(np.array([lanelet_start_pos_x, lanelet_start_pos_y]), 0)
            if not self.road_network_toolbox_ui.horizontal.isChecked():
                if self.road_network_toolbox_ui.select_end_position.isChecked():
                    rotation_angle = math.degrees(
                            math.asin((self.get_y_position_lanelet_end() - lanelet_start_pos_y) / lanelet_length))
                    # convert rotation_angle to positive angle since translate_rotate function only expects positive
                    # angle
                    if self.get_x_position_lanelet_end() < lanelet_start_pos_x:
                        rotation_angle = 180 - rotation_angle
                    if rotation_angle < 0:
                        rotation_angle = 360 + rotation_angle
                elif self.road_network_toolbox_ui.rotate.isChecked():
                    rotation_angle = int(self.road_network_toolbox_ui.rotation_angle_end.text())

                initial_vertex_x = lanelet.center_vertices[0]
                if rotation_angle > 360:
                    rotation_angle %= 360
                lanelet.translate_rotate(np.array([0, 0]), np.deg2rad(rotation_angle))
                lanelet.translate_rotate(initial_vertex_x - lanelet.center_vertices[0], 0.0)

        self.road_network_controller.last_added_lanelet_id = lanelet_id

        # uncheck all buttons and hide all selected boxes
        self.road_network_toolbox_ui.connecting_radio_button_group.setExclusive(False)
        if self.road_network_toolbox_ui.place_at_position.isChecked():
            self.road_network_toolbox_ui.place_at_position.click()
        elif self.road_network_toolbox_ui.connect_to_previous_selection.isChecked():
            self.road_network_toolbox_ui.connect_to_previous_selection.click()
        elif self.road_network_toolbox_ui.connect_to_predecessors_selection.isChecked():
            self.road_network_toolbox_ui.connect_to_predecessors_selection.click()
        elif self.road_network_toolbox_ui.connect_to_successors_selection.isChecked():
            self.road_network_toolbox_ui.connect_to_successors_selection.click()
        self.road_network_toolbox_ui.connecting_radio_button_group.setExclusive(True)

        self.scenario_model.add_lanelet(lanelet)
        self.road_network_controller.initialize_road_network_toolbox()

    def update_lanelet(self):
        """
        Updates a given lanelet based on the information configured by the user.
        """

        selected_lanelet = self.selected_lanelet()
        if selected_lanelet is None:
            return
        old_lanelet_id = selected_lanelet.lanelet_id
        new_lanelet = self.add_updated_lanelet(old_lanelet_id, selected_lanelet.left_vertices,
                                               selected_lanelet.right_vertices)

        self.road_network_controller.updated_lanelet = True
        self.scenario_model.update_lanelet(old_lanelet_id, selected_lanelet, new_lanelet)
        self.road_network_controller.set_default_road_network_list_information()

    def add_updated_lanelet(self, lanelet_id: int, left_vertices: np.array = None, right_vertices: np.array = None):
        """
                Adds an updated lanelet to the scenario based on the selected parameters by the user.
                The original lanelet has to be removed beforeward.

                @param lanelet_id: Id which the new lanelet should have.
                @param update: Boolean indicating whether lanelet is updated or newly created.
                @param left_vertices: Left boundary of lanelet which should be updated.
                @param right_vertices: Right boundary of lanelet which should be updated.
                """
        predecessors = [int(pre) for pre in self.road_network_toolbox_ui.selected_predecessors.get_checked_items()]
        successors = [int(suc) for suc in self.road_network_toolbox_ui.selected_successors.get_checked_items()]

        lanelet_start_pos_x = self.get_x_position_lanelet_start(True)
        lanelet_start_pos_y = self.get_y_position_lanelet_start(True)
        lanelet_end_pos_x = self.get_x_position_lanelet_end(True)
        lanelet_end_pos_y = self.get_y_position_lanelet_end(True)

        lanelet_width = self.road_network_controller.get_float(self.road_network_toolbox_ui.selected_lanelet_width)
        line_marking_left = LineMarking(self.road_network_toolbox_ui.selected_line_marking_left.currentText())
        line_marking_right = LineMarking(self.road_network_toolbox_ui.selected_line_marking_right.currentText())
        num_vertices = int(self.road_network_toolbox_ui.selected_number_vertices.text())
        adjacent_left = int(
                self.road_network_toolbox_ui.selected_adjacent_left.currentText()) if \
            self.road_network_toolbox_ui.selected_adjacent_left.currentText() != "None" else None
        adjacent_right = int(
                self.road_network_toolbox_ui.selected_adjacent_right.currentText()) if \
            self.road_network_toolbox_ui.selected_adjacent_right.currentText() != "None" else None
        adjacent_left_same_direction = self.road_network_toolbox_ui.selected_adjacent_left_same_direction.isChecked()
        adjacent_right_same_direction = self.road_network_toolbox_ui.selected_adjacent_right_same_direction.isChecked()
        lanelet_type = {LaneletType(ty) for ty in self.road_network_toolbox_ui.selected_lanelet_type.get_checked_items()
                        if ty != "None"}
        user_one_way = {RoadUser(user) for user in
                        self.road_network_toolbox_ui.selected_road_user_oneway.get_checked_items() if user != "None"}
        user_bidirectional = {RoadUser(user) for user in
                              self.road_network_toolbox_ui.selected_road_user_bidirectional.get_checked_items() if
                              user != "None"}

        traffic_signs = {int(sign) for sign in
                         self.road_network_toolbox_ui.selected_lanelet_referenced_traffic_sign_ids.get_checked_items()}
        traffic_lights = {int(light) for light in
                          self.road_network_toolbox_ui.selected_lanelet_referenced_traffic_light_ids
                          .get_checked_items()}
        if self.road_network_toolbox_ui.selected_stop_line_box.isChecked():
            if self.road_network_toolbox_ui.selected_stop_line_beginning.isChecked():
                stop_line_at_end = False
                stop_line_at_beginning = True
                stop_line_marking = LineMarking(
                        self.road_network_toolbox_ui.selected_line_marking_stop_line.currentText())
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
            elif self.road_network_toolbox_ui.selected_stop_line_end.isChecked():
                stop_line_at_end = True
                stop_line_at_beginning = False
                stop_line_marking = LineMarking(
                        self.road_network_toolbox_ui.selected_line_marking_stop_line.currentText())
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
            else:
                stop_line_start_x = self.road_network_controller \
                    .get_float(self.road_network_toolbox_ui.selected_stop_line_start_x)
                stop_line_end_x = self.road_network_controller \
                    .get_float(self.road_network_toolbox_ui.selected_stop_line_end_x)
                stop_line_start_y = self.road_network_controller \
                    .get_float(self.road_network_toolbox_ui.selected_stop_line_start_y)
                stop_line_end_y = self.road_network_controller \
                    .get_float(self.road_network_toolbox_ui.selected_stop_line_end_y)
                stop_line_marking = LineMarking(
                        self.road_network_toolbox_ui.selected_line_marking_stop_line.currentText())
                stop_line_at_end = False
                stop_line_at_beginning = False
                stop_line = StopLine(np.array([stop_line_start_x, stop_line_start_y]),
                                     np.array([stop_line_end_x, stop_line_end_y]), stop_line_marking, set(), set())
        else:
            stop_line_at_end = False
            stop_line_at_beginning = False
            stop_line = None

        lanelet_length = self.road_network_controller.get_float(self.road_network_toolbox_ui.selected_lanelet_length)
        lanelet_radius = self.road_network_controller.get_float(self.road_network_toolbox_ui.selected_lanelet_radius)
        lanelet_angle = np.deg2rad(self.road_network_controller
                                   .get_float(self.road_network_toolbox_ui.selected_lanelet_angle))
        add_curved_selection = self.road_network_toolbox_ui.selected_curved_checkbox.button.isChecked()

        if stop_line is not None:
            stop_line_start = stop_line.start
            stop_line_end = stop_line.end

        if add_curved_selection:
            lanelet = MapCreator.create_curve(lanelet_width, lanelet_radius, lanelet_angle, num_vertices, lanelet_id,
                                              lanelet_type, predecessors, successors, adjacent_left, adjacent_right,
                                              adjacent_left_same_direction, adjacent_right_same_direction, user_one_way,
                                              user_bidirectional, line_marking_left, line_marking_right, stop_line,
                                              traffic_signs, traffic_lights, stop_line_at_end, stop_line_at_beginning)
            rotation_angle = 0
        else:
            lanelet = MapCreator.create_straight(lanelet_width, lanelet_length, num_vertices, lanelet_id, lanelet_type,
                                                 predecessors, successors, adjacent_left, adjacent_right,
                                                 adjacent_left_same_direction, adjacent_right_same_direction,
                                                 user_one_way, user_bidirectional, line_marking_left,
                                                 line_marking_right, stop_line, traffic_signs, traffic_lights,
                                                 stop_line_at_end, stop_line_at_beginning)
            rotation_angle = math.degrees(math.asin((lanelet_end_pos_y - lanelet_start_pos_y) / lanelet_length))

        lanelet.translate_rotate(np.array([lanelet_start_pos_x, lanelet_start_pos_y]), 0)

        # convert rotation_angle to positive angle since translate_rotate function only expects positive
        # angle
        if lanelet_end_pos_x < lanelet_start_pos_x:
            rotation_angle = 180 - rotation_angle
        if rotation_angle < 0:
            rotation_angle = 360 + rotation_angle

        initial_vertex = lanelet.center_vertices[0]
        lanelet.translate_rotate(np.array([0, 0]), np.deg2rad(rotation_angle))
        lanelet.translate_rotate(initial_vertex - lanelet.center_vertices[0], 0.0)

        # rotation destroys position of stop line therefore save stop line position and afterwards set stop line
        # position again to right value
        if stop_line is not None and not stop_line_at_end and not stop_line_at_beginning:
            lanelet.stop_line.start = stop_line_start
            lanelet.stop_line.end = stop_line_end

        self.road_network_controller.last_added_lanelet_id = lanelet_id
        return lanelet

    def remove_lanelet(self):
        """
               Removes a selected lanelet from the scenario.
               """
        selected_lanelet = self.selected_lanelet()
        if selected_lanelet is None:
            return

        if selected_lanelet.lanelet_id == self.road_network_controller.last_added_lanelet_id:
            self.road_network_controller.last_added_lanelet_id = None

        self.scenario_model.remove_lanelet(selected_lanelet.lanelet_id)
        self.road_network_controller.set_default_road_network_list_information()

    def attach_to_other_lanelet(self):
        """
                Attaches a lanelet to another lanelet.
                @return:
                """
        selected_lanelet_one = self.selected_lanelet()
        if selected_lanelet_one is None:
            return
        if self.road_network_toolbox_ui.selected_lanelet_two.currentText() != "None":
            selected_lanelet_two = self.scenario_model.find_lanelet_by_id(
                    int(self.road_network_toolbox_ui.selected_lanelet_two.currentText()))
        else:
            self.road_network_controller.text_browser.append("No lanelet selected for [2].")
            return

        self.scenario_model.attach_to_other_lanelet(selected_lanelet_one, selected_lanelet_two)

    def create_adjacent(self):
        """
        Create adjacent lanelet given a selected lanelet
        """
        selected_lanelet = self.selected_lanelet()
        if selected_lanelet is None:
            return
        if selected_lanelet.predecessor:
            self.road_network_controller.text_browser.append(selected_lanelet.predecessor.pop())
        if selected_lanelet.successor:
            self.road_network_controller.text_browser.append(selected_lanelet.successor.pop())
        if selected_lanelet is None:
            return

        adjacent_left = self.road_network_toolbox_ui.create_adjacent_left_selection.isChecked()
        adjacent_same_direction = self.road_network_toolbox_ui.create_adjacent_same_direction_selection.isChecked()
        lanelet_width = float(str(np.linalg.norm(selected_lanelet.left_vertices[0]-selected_lanelet.right_vertices[0])))
        line_marking_left = selected_lanelet.line_marking_left_vertices
        line_marking_right = selected_lanelet.line_marking_right_vertices
        predecessors = selected_lanelet.predecessor
        successors = selected_lanelet.successor
        lanelet_type = selected_lanelet.lanelet_type
        user_one_way = selected_lanelet.user_one_way
        user_bidirectional = selected_lanelet.user_bidirectional
        traffic_signs = selected_lanelet.traffic_signs
        traffic_lights = selected_lanelet.traffic_lights
        stop_line_at_end = False
        stop_line = None
        if selected_lanelet.stop_line is not None:
            stop_line_marking = selected_lanelet.stop_line.line_marking
            if all(selected_lanelet.stop_line.start == selected_lanelet.left_vertices[0]) and all(
                    selected_lanelet.stop_line.end == selected_lanelet.right_vertices[0]):
                # stop line at beginning
                stop_line_at_end = False
                stop_line_at_beginning = True
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
            elif all(selected_lanelet.stop_line.start == selected_lanelet.left_vertices[
                len(selected_lanelet.left_vertices) - 1]) and all(
                    selected_lanelet.stop_line.end == selected_lanelet.right_vertices[
                        len(selected_lanelet.right_vertices) - 1]):
                stop_line_at_end = True
                stop_line_at_beginning = False
                stop_line = StopLine(np.array([0, 0]), np.array([0, 0]), stop_line_marking, set(), set())
            else:
                stop_line_start_x = selected_lanelet.stop_line.start[0]
                stop_line_end_x = selected_lanelet.stop_line.end[0]
                stop_line_start_y = selected_lanelet.stop_line.start[1]
                stop_line_end_y = selected_lanelet.stop_line.end[1]
                stop_line = StopLine(np.array([stop_line_start_x, stop_line_start_y]),
                                     np.array([stop_line_end_x, stop_line_end_y]), stop_line_marking, set(), set())

        if adjacent_left:
            adjacent_lanelet = MapCreator.create_adjacent_lanelet(adjacent_left, selected_lanelet,
                                                                  self.scenario_model.generate_object_id(),
                                                                  adjacent_same_direction, lanelet_width, lanelet_type,
                                                                  predecessors, successors, user_one_way,
                                                                  user_bidirectional, line_marking_left,
                                                                  line_marking_right, stop_line, traffic_signs,
                                                                  traffic_lights, stop_line_at_end)
        else:
            adjacent_lanelet = MapCreator.create_adjacent_lanelet(adjacent_left, selected_lanelet,
                                                                  self.scenario_model.generate_object_id(),
                                                                  adjacent_same_direction, lanelet_width, lanelet_type,
                                                                  predecessors, successors, user_one_way,
                                                                  user_bidirectional, line_marking_left,
                                                                  line_marking_right, stop_line, traffic_signs,
                                                                  traffic_lights, stop_line_at_end)

        if adjacent_lanelet is not None:
            self.last_added_lanelet_id = adjacent_lanelet.lanelet_id
            self.scenario_model.add_lanelet(adjacent_lanelet)
            self.road_network_controller.set_default_road_network_list_information()
        else:
            self.road_network_controller.text_browser.append("Adjacent lanelet already exists.")

    def connect_lanelets(self):
        """
        Connects two lanelets by adding a new lanelet using cubic spline interpolation.
        """
        selected_lanelet_one = self.selected_lanelet()
        if selected_lanelet_one is None:
            return
        if self.road_network_toolbox_ui.selected_lanelet_two.currentText() != "None":
            selected_lanelet_two = self.scenario_model.find_lanelet_by_id(
                    int(self.road_network_toolbox_ui.selected_lanelet_two.currentText()))
        else:
            self.road_network_controller.text_browser.append("No lanelet selected for [2].")
            return

        connected_lanelet = MapCreator.connect_lanelets(selected_lanelet_one, selected_lanelet_two,
                                                        self.scenario_model.generate_object_id())

        self.road_network_controller.last_added_lanelet_id = connected_lanelet.lanelet_id
        self.scenario_model.add_lanelet(connected_lanelet)
        self.road_network_controller.set_default_road_network_list_information()

    def rotate_lanelet(self):
        """
        Rotates lanelet by a user-defined angle.
        """
        selected_lanelet_one = self.selected_lanelet()
        if selected_lanelet_one is None:
            return
        rotation_angle = int(self.road_network_toolbox_ui.rotation_angle.text())
        self.scenario_model.rotate_lanelet(selected_lanelet_one, rotation_angle)

    def translate_lanelet(self):
        """
        Translates lanelet by user-defined x- and y-values.
        """
        selected_lanelet_one = self.selected_lanelet()
        if selected_lanelet_one is None:
            return
        x_translation = self.road_network_controller.get_float(self.road_network_toolbox_ui.x_translation)
        y_translation = self.road_network_controller.get_float(self.road_network_toolbox_ui.y_translation)
        selected_lanelet_one.translate_rotate(np.array([x_translation, y_translation]), 0)

        self.scenario_model.translate_lanelet(selected_lanelet_one)

    def merge_with_successor(self):
        """
         Merges a lanelet with its successor. If several successors exist, a new lanelet is created for each successor.
        """
        selected_lanelet_one = self.selected_lanelet()
        if selected_lanelet_one is None:
            return
        self.scenario_model.merge_with_successor(selected_lanelet_one)

    def get_x_position_lanelet_start(self, update=False) -> float:
        """
        Extracts lanelet x-position of first center vertex.

        @return: x-position [m]
        """
        if not update:
            if self.road_network_toolbox_ui.place_at_position.isChecked() and \
                    self.road_network_toolbox_ui.lanelet_start_position_x.text() and \
                    self.road_network_toolbox_ui.lanelet_start_position_x.text() != "-":
                return float(self.road_network_toolbox_ui.lanelet_start_position_x.text().replace(",", "."))
            else:
                return 0
        else:
            if self.road_network_toolbox_ui.selected_lanelet_start_position_x.text() and \
                    self.road_network_toolbox_ui.selected_lanelet_start_position_x.text() != "-":
                return float(
                    self.road_network_toolbox_ui.selected_lanelet_start_position_x.text().replace(",", "."))
            else:
                return 0

    def get_y_position_lanelet_start(self, update=False) -> float:
        """
        Extracts lanelet y-position of first center vertex.

        @return: y-position [m]
        """
        if not update:
            if self.road_network_toolbox_ui.place_at_position.isChecked() and \
                    self.road_network_toolbox_ui.lanelet_start_position_y.text() and \
                    self.road_network_toolbox_ui.lanelet_start_position_y.text() != "-":
                return float(self.road_network_toolbox_ui.lanelet_start_position_y.text().replace(",", "."))
            else:
                return 0
        else:
            if self.road_network_toolbox_ui.selected_lanelet_start_position_y.text() and \
                    self.road_network_toolbox_ui.selected_lanelet_start_position_y.text() != "-":
                return float(
                    self.road_network_toolbox_ui.selected_lanelet_start_position_y.text().replace(",", "."))
            else:
                return 0

    def get_x_position_lanelet_end(self, update=False) -> float:
        """
        Extracts lanelet x-position of last center vertex.

        @return: x-position [m]
        """
        if not update:
            if self.road_network_toolbox_ui.lanelet_end_position_x.text() and \
                    self.road_network_toolbox_ui.lanelet_end_position_x.text() != "-":
                return float(self.road_network_toolbox_ui.lanelet_end_position_x.text().replace(",", "."))
            else:
                return 0
        else:
            if self.road_network_toolbox_ui.selected_lanelet_end_position_x.text() and \
                    self.road_network_toolbox_ui.selected_lanelet_end_position_x.text() != "-":
                return float(self.road_network_toolbox_ui.selected_lanelet_end_position_x.text().replace(",", "."))
            else:
                return 0

    def get_y_position_lanelet_end(self, update=False) -> float:
        """
        Extracts lanelet y-position of last center vertex.

        @return: y-position [m]
        """
        if not update:
            if self.road_network_toolbox_ui.lanelet_end_position_y.text() and \
                    self.road_network_toolbox_ui.lanelet_end_position_y.text() != "-":
                return float(self.road_network_toolbox_ui.lanelet_end_position_y.text().replace(",", "."))
            else:
                return 0
        else:
            if self.road_network_toolbox_ui.selected_lanelet_end_position_y.text() and \
                    self.road_network_toolbox_ui.selected_lanelet_end_position_y.text() != "-":
                return float(self.road_network_toolbox_ui.selected_lanelet_end_position_y.text().replace(",", "."))
            else:
                return 0

    def selected_lanelet(self) -> Union[Lanelet, None]:
        """
        Extracts the selected lanelet one
        @return: Selected lanelet object.
        """
        if not self.road_network_controller.initialized:
            return
        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("create a new file")
            return None
        if self.road_network_toolbox_ui.selected_lanelet_update.currentText() not in ["None", ""]:
            selected_lanelet = self.scenario_model.find_lanelet_by_id(
                    int(self.road_network_toolbox_ui.selected_lanelet_update.currentText()))
            return selected_lanelet
        elif self.road_network_toolbox_ui.selected_lanelet_update.currentText() in ["None", ""] and not \
                self.road_network_controller.update:
            self.road_network_controller.text_browser.append("No lanelet selected.")
            return None
