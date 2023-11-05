from PyQt5.QtWidgets import QTableWidgetItem, QComboBox
from commonroad.scenario.intersection import IncomingGroup, Intersection

from crdesigner.ui.gui.model.scenario_model import ScenarioModel
from crdesigner.ui.gui.utilities.toolbox_ui import CheckableComboBox
from crdesigner.ui.gui.view.toolboxes.road_network_toolbox.intersections_ui import AddIntersectionUI
from crdesigner.ui.gui.view.toolboxes.road_network_toolbox.road_network_toolbox_ui.road_network_toolbox_ui import \
    RoadNetworkToolboxUI
from commonroad.scenario.traffic_sign import *
from PyQt5.QtWidgets import *


class AddIntersectionController:

    def __init__(self, road_network_controller, scenario_model: ScenarioModel,
                 road_network_toolbox_ui: RoadNetworkToolboxUI):
        self.scenario_model = scenario_model
        self.road_network_toolbox_ui = road_network_toolbox_ui
        self.road_network_controller = road_network_controller
        self.intersection_ui = AddIntersectionUI(self.scenario_model, self.road_network_toolbox_ui)

    def connect_gui_intersection(self):
        self.road_network_toolbox_ui.button_four_way_intersection.clicked.connect(
                lambda: self.add_four_way_intersection())
        self.road_network_toolbox_ui.button_three_way_intersection.clicked.connect(
                lambda: self.add_three_way_intersection())
        self.road_network_toolbox_ui.selected_intersection.currentTextChanged.connect(
                lambda: self.intersection_ui.update_intersection_information())
        self.road_network_toolbox_ui.button_add_incoming.clicked.connect(
            lambda: self.intersection_ui.add_incoming_to_table())
        self.road_network_toolbox_ui.button_remove_incoming.clicked.connect(
                lambda: self.intersection_ui.remove_incoming())
        self.road_network_toolbox_ui.button_fit_intersection.clicked.connect(lambda: self.fit_intersection())
        self.road_network_toolbox_ui.button_add_intersection.clicked.connect(lambda: self.add_intersection())
        self.road_network_toolbox_ui.button_remove_intersection.clicked.connect(lambda: self.remove_intersection())
        self.road_network_toolbox_ui.button_update_intersection.clicked.connect(lambda: self.update_intersection())
        self.road_network_toolbox_ui.button_rotate_intersection.clicked.connect(lambda: self.rotate_intersection())
        self.road_network_toolbox_ui.button_translate_intersection.clicked.connect(
            lambda: self.translate_intersection())

    def add_four_way_intersection(self):
        """
        Adds a four-way intersection to the scenario.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("_Warning:_ Create a new file")
            return
        width = self.road_network_controller.get_float(self.road_network_toolbox_ui.intersection_lanelet_width)
        diameter = int(self.road_network_toolbox_ui.intersection_diameter.text())
        incoming_length = int(self.road_network_toolbox_ui.intersection_incoming_length.text())
        add_traffic_signs = self.road_network_toolbox_ui.intersection_with_traffic_signs.isChecked()
        add_traffic_lights = self.road_network_toolbox_ui.intersection_with_traffic_lights.isChecked()

        x_pos_content = self.road_network_toolbox_ui.intersection_start_position_x.text()
        y_pos_content = self.road_network_toolbox_ui.intersection_start_position_y.text()
        x_pos = float(x_pos_content) if x_pos_content is not None and x_pos_content != '' else 0
        y_pos = float(y_pos_content) if y_pos_content is not None and y_pos_content != '' else 0

        self.scenario_model.create_four_way_intersection(width, diameter, incoming_length, add_traffic_signs,
                                                         add_traffic_lights, x_pos, y_pos)

        self.road_network_controller.set_default_road_network_list_information()

    def add_three_way_intersection(self):
        """
        Adds a three-way intersection to the scenario.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("_Warning:_ Create a new file")
            return
        width = self.road_network_controller.get_float(self.road_network_toolbox_ui.intersection_lanelet_width)
        diameter = int(self.road_network_toolbox_ui.intersection_diameter.text())
        incoming_length = int(self.road_network_toolbox_ui.intersection_incoming_length.text())
        add_traffic_signs = self.road_network_toolbox_ui.intersection_with_traffic_signs.isChecked()
        add_traffic_lights = self.road_network_toolbox_ui.intersection_with_traffic_lights.isChecked()

        x_pos_content = self.road_network_toolbox_ui.intersection_start_position_x.text()
        y_pos_content = self.road_network_toolbox_ui.intersection_start_position_y.text()
        x_pos = float(x_pos_content) if x_pos_content is not None and x_pos_content != '' else 0
        y_pos = float(y_pos_content) if y_pos_content is not None and y_pos_content != '' else 0

        self.scenario_model.create_three_way_intersection(width, diameter, incoming_length, add_traffic_signs,
                                                          add_traffic_lights, x_pos, y_pos)
        self.road_network_controller.set_default_road_network_list_information()

    def fit_intersection(self):
        """
         Rotates and translates a complete intersection so that it is attached to a user-defined lanelet.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if (self.road_network_toolbox_ui.selected_intersection.currentText() not in ["",
                                                                                    "None"] and
                self.road_network_toolbox_ui.other_lanelet_to_fit.currentText() not in [
            "", "None"] and self.road_network_toolbox_ui.intersection_lanelet_to_fit.currentText() not in ["", "None"]):
            selected_intersection_id = int(self.road_network_toolbox_ui.selected_intersection.currentText())
            predecessor_id = int(self.road_network_toolbox_ui.other_lanelet_to_fit.currentText())
            successor_id = int(self.road_network_toolbox_ui.intersection_lanelet_to_fit.currentText())

            self.scenario_model.fit_intersection(selected_intersection_id, predecessor_id, successor_id)

    def add_intersection(self, intersection_id: int = None):
        """
        Adds an intersection to the scenario.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("_Warning:_ Create a new file")
            return

        if intersection_id is None:
            intersection_id = self.scenario_model.generate_object_id()
        incomings = []
        for row in range(self.road_network_toolbox_ui.intersection_incomings_table.rowCount()):
            incoming_id = int(self.road_network_toolbox_ui.intersection_incomings_table.item(row, 0).text())
            incoming_lanelets = {int(item) for item in
                                 self.road_network_toolbox_ui.intersection_incomings_table.cellWidget(row,
                                                                                                      1).get_checked_items()}
            if len(incoming_lanelets) < 1:
                self.road_network_controller.text_browser.append("_Warning:_ An incoming must consist at least of one lanelet.")
                print("intersections_controller.py/add_intersection: An incoming must consist at least of one lanelet.")
                return
            successor_left = {int(item) for item in
                              self.road_network_toolbox_ui.intersection_incomings_table.cellWidget(row,
                                      2).get_checked_items()}
            successor_straight = {int(item) for item in
                                  self.road_network_toolbox_ui.intersection_incomings_table.cellWidget(row,
                                          3).get_checked_items()}
            successor_right = {int(item) for item in
                               self.road_network_toolbox_ui.intersection_incomings_table.cellWidget(row,
                                       4).get_checked_items()}
            if len(successor_left) + len(successor_right) + len(successor_straight) < 1:
                print("An incoming must consist at least of one successor")
                return
            left_of = int(self.road_network_toolbox_ui.intersection_incomings_table.cellWidget(row
                                                                                               ,5)
                          .currentText()) if self.road_network_toolbox_ui.intersection_incomings_table\
                                                                       .cellWidget \
                (row, 5).currentText() != "" else None
            incoming = IncomingGroup(incoming_id=incoming_id,
                                     incoming_lanelets=incoming_lanelets,
                                     outgoing_right=successor_right,
                                     outgoing_straight=successor_straight,
                                     outgoing_left=successor_left)
            incomings.append(incoming)
        crossings = {int(item) for item in self.road_network_toolbox_ui.intersection_crossings.get_checked_items()}

        if len(incomings) > 1:
            intersection = Intersection(intersection_id, incomings)
            self.scenario_model.add_intersection(intersection)
            self.road_network_controller.set_default_road_network_list_information()
        else:
            self.road_network_controller.text_browser \
                .append \
                ("_Warning:_ An intersection must consist at least of two incomings.")
            print("intersections_controller.py/add_intersection: An intersection must consist at least of two "
                  "incomings.")

    def remove_intersection(self):
        """
        Removes selected intersection from lanelet network.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("_Warning:_ Create a new file")
            return

        if self.road_network_toolbox_ui.selected_intersection.currentText() not in ["", "None"]:
            selected_intersection_id = int(self.road_network_toolbox_ui.selected_intersection.currentText())
            self.scenario_model.remove_intersection(selected_intersection_id)
            self.road_network_controller.set_default_road_network_list_information()

    def update_intersection(self):
        """
        Updates a selected intersection from the scenario.
        """
        if self.road_network_controller.mwindow.play_activated:
            self.road_network_controller.text_browser.append("Please stop the animation first.")
            return

        if not self.scenario_model.scenario_created():
            self.road_network_controller.text_browser.append("_Warning:_ Create a new file")
            return

        if self.road_network_toolbox_ui.selected_intersection.currentText() not in ["", "None"]:
            selected_intersection_id = int(self.road_network_toolbox_ui.selected_intersection.currentText())
            self.scenario_model.update_intersection(selected_intersection_id)
            self.add_intersection(selected_intersection_id)

    def rotate_intersection(self):
        """
        _summary_: translate intersections by user-defined x- and y-values.
        """

        # Getting rotation details.

        if self.road_network_toolbox_ui.selected_intersection.currentText() in ["", "None"]:
            self.road_network_controller.text_browser.append("Please select an intersection first.")
            return

        try:
            angle = float(self.road_network_toolbox_ui.intersection_rotation_angle.text())
        except ValueError:
            return

        # Finding intersection.
        selected_intersection_id = int(self.road_network_toolbox_ui.selected_intersection.currentText())
        intersection = self.scenario_model.find_intersection_by_id(selected_intersection_id)

        lanelets = self.collect_lanelets(intersection)

        for lanelet_id in lanelets:
            lanelet = self.scenario_model.find_lanelet_by_id(lanelet_id)
            lanelet.translate_rotate(np.array([0, 0]), np.deg2rad(angle))

        self.update_intersection()
        self.road_network_controller.set_default_road_network_list_information()

    def translate_intersection(self):
        """
        _summary_: translate intersections by user-defined x- and y-values.
        """

        # Getting rotation details.

        if self.road_network_toolbox_ui.selected_intersection.currentText() in ["", "None"]:
            self.road_network_controller.text_browser.append("Please select an intersection first.")
            return

        try:
            x = float(self.road_network_toolbox_ui.intersection_x_translation.text())
        except ValueError:
            x = 0

        try:
            y = float(self.road_network_toolbox_ui.intersection_y_translation.text())
        except ValueError:
            y = 0

        # Finding intersection.
        selected_intersection_id = int(self.road_network_toolbox_ui.selected_intersection.currentText())
        intersection = self.scenario_model.find_intersection_by_id(selected_intersection_id)

        lanelets = self.collect_lanelets(intersection)

        for lanelet_id in lanelets:
            lanelet = self.scenario_model.find_lanelet_by_id(lanelet_id)
            lanelet.translate_rotate(np.array([x, y]), np.deg2rad(0))

        self.update_intersection()
        self.road_network_controller.set_default_road_network_list_information()

    def collect_lanelets(self, intersection: Intersection) -> Set[int]:
        lanelets = []
        for incoming_group in intersection.incomings:
            lanelets += list(incoming_group.incoming_lanelets)
            lanelets += list(incoming_group.outgoing_left)
            lanelets += list(incoming_group.outgoing_right)
            lanelets += list(incoming_group.outgoing_straight)

        if intersection.outgoings is not None:
            for outgoing_group in intersection.outgoings:
                if outgoing_group.outgoing_lanelets is not None:
                    lanelets += list(outgoing_group.outgoing_lanelets)

        return set(lanelets)
