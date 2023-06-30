import logging
import os
import sys
from typing import Optional

from PyQt5.QtWidgets import *
from commonroad.common.file_writer import CommonRoadFileWriter, OverwriteExistingFile

from crdesigner.ui.gui.model.scenario_model import ScenarioModel
from crdesigner.ui.gui.view.settings.scenario_saving_dialog_ui import ScenarioSavingDialogUI
from commonroad.planning.planning_problem import PlanningProblemSet
from commonroad.common.common_scenario import TimeOfDay, Weather, Underground, Time, Location
from commonroad.scenario.scenario import Environment, Tag, Scenario

from crdesigner.ui.gui.autosaves.autosaves_setup import DIR_AUTOSAVE


class ScenarioSavingDialogController:

    def __init__(self):
        self.save_window = ScenarioSavingDialogUI()
        self.connect_gui_elements()
        self.current_scenario: Optional[ScenarioModel] = None
        self.current_pps: Optional[PlanningProblemSet] = None
        self.directory = ""
        self.initialized = False

    def connect_gui_elements(self):
        self.save_window.country.currentTextChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.scenario_scene_name.textChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.scenario_scene_id.valueChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.scenario_config_id.valueChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.prediction_type.currentTextChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.scenario_prediction_id.valueChanged.connect(lambda: self.update_scenario_meta_data())
        self.save_window.cooperative_scenario.stateChanged.connect(lambda: self.update_scenario_meta_data())

        self.save_window.button_directory.clicked.connect(lambda: self.select_directory())
        self.save_window.button_save.clicked.connect(lambda: self.save_scenario())

    def show(self, scenario: ScenarioModel, pps: PlanningProblemSet):
        self.initialized = False
        self.current_scenario = scenario.get_current_scenario()
        self.current_pps = pps
        self.save_window.label_benchmark_id.setText(self.current_scenario.scenario_id.__str__())

        self.save_window.scenario_author.setText(self.current_scenario.file_information.author)
        self.save_window.scenario_affiliation.setText(self.current_scenario.file_information.affiliation)
        self.save_window.scenario_source.setText(self.current_scenario.file_information.source)
        self.save_window.scenario_time_step_size.setText(str(self.current_scenario.dt))
        self.save_window.scenario_tags.set_checked_items(
                [t.value for t in self.current_scenario.tags] if self.current_scenario.tags else [])
        self.save_window.scenario_config_id.setValue(
                self.current_scenario.scenario_id.configuration_id if
                self.current_scenario.scenario_id.configuration_id else 1)
        self.save_window.cooperative_scenario.setChecked(
                self.current_scenario.scenario_id.cooperative if self.current_scenario.scenario_id.cooperative else
                False)
        self.save_window.country.setCurrentText(self.current_scenario.scenario_id.country_id)
        self.save_window.scenario_scene_id.setValue(self.current_scenario.scenario_id.map_id)
        self.save_window.scenario_scene_name.setText(self.current_scenario.scenario_id.map_name)
        self.save_window.prediction_type.setCurrentText(self.current_scenario.scenario_id.obstacle_behavior)
        self.save_window.scenario_prediction_id.setValue(
                self.current_scenario.scenario_id.prediction_id if self.current_scenario.scenario_id.prediction_id
                else 1)

        if self.current_scenario.lanelet_network.location:
            self.save_window.scenario_geo_anme_id.setText(str(self.current_scenario.lanelet_network.location.geo_name_id))
            self.save_window.scenario_latitude.setText(str(self.current_scenario.lanelet_network.location.gps_latitude))
            self.save_window.scenario_longitude.setText(str(self.current_scenario.lanelet_network.location.gps_longitude))
            if self.current_scenario.environment:
                self.save_window.scenario_time_of_day.setCurrentText(
                        self.current_scenario.environment.time_of_day.value)
                self.save_window.scenario_weather.setCurrentText(
                        self.current_scenario.environment.weather.value)
                self.save_window.scenario_underground.setCurrentText(
                        self.current_scenario.environment.underground.value)
                self.save_window.scenario_time_hour.setValue(self.current_scenario.environment.time.hours)
                self.save_window.scenario_time_minute.setValue(self.current_scenario.environment.time.minutes)
            else:
                self.init_scenario_location_default()
        else:
            self.save_window.scenario_geo_anme_id.setText("-999")
            self.save_window.scenario_latitude.setText("999")
            self.save_window.scenario_longitude.setText("999")
            self.init_scenario_location_default()
        self.save_window.show()
        self.initialized = True

    def init_scenario_location_default(self):
        self.save_window.scenario_time_of_day.setCurrentText(TimeOfDay.UNKNOWN.value)
        self.save_window.scenario_weather.setCurrentText(Weather.UNKNOWN.value)
        self.save_window.scenario_underground.setCurrentText(Underground.UNKNOWN.value)
        self.save_window.scenario_time_hour.setValue(0)
        self.save_window.scenario_time_minute.setValue(0)

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self.save_window, "Dir", options=QFileDialog.Options())
        if dir:
            self.save_window.label_directory.setText(self.directory)

    def autosave(self, scenario: Scenario):
        '''
        Saves the file in a background file with default parameters

        Disables the console output of the write to file methode that there is no clutter in the console
        Enables it afterwards again

        :param scenario: Scenario which should be saved
        '''
        try:
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            original_level = logging.getLogger().getEffectiveLevel()
            logging.getLogger().setLevel(logging.ERROR)
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = open(os.devnull, 'w')
            writer = CommonRoadFileWriter(scenario=scenario, planning_problem_set=self.current_pps,
                                          author="Default Author",
                                          affiliation="Default Affiliation",
                                          source="CommonRoad Scenario Designer",
                                          tags=set())
            filename = DIR_AUTOSAVE + "/autosave" + ".xml"
            if self.current_pps is None:
                writer.write_scenario_to_file(filename, OverwriteExistingFile.ALWAYS)
            else:
                writer.write_to_file(filename, OverwriteExistingFile.ALWAYS)
            sys.stdout = original_stdout
            sys.stderr = original_stderr
            logging.getLogger().setLevel(original_level)
        except IOError as e:
            pass

    def save_scenario(self):
        self.update_scenario_meta_data()
        try:
            writer = CommonRoadFileWriter(scenario=self.current_scenario.get_current_scenario(),
                                          planning_problem_set=self.current_pps,
                                          author=self.current_scenario.get_current_scenario().file_information.author,
                                          affiliation=self.current_scenario.get_current_scenario().file_information.affiliation,
                                          source=self.current_scenario.get_current_scenario().file_information.source,
                                          tags=set(self.current_scenario.get_current_scenario().tags), )
            filename = self.directory + "/" + self.current_scenario.get_current_scenario().scenario_id.__str__() \
                + ".xml"
            if self.current_pps is None:
                writer.write_scenario_to_file(filename, OverwriteExistingFile.ALWAYS)
            else:
                writer.write_to_file(filename, OverwriteExistingFile.ALWAYS)
            self.save_window.close()
            filename_autosave = DIR_AUTOSAVE + "/autosave" + ".xml"
            if os.path.exists(filename_autosave):
                os.remove(filename_autosave)
        except IOError as e:
            QMessageBox.critical(self.save_window, "CommonRoad file not created!",
                                 "The CommonRoad file was not saved due to an error.\n\n" + "{}".format(e),
                                 QMessageBox.Ok, )

    def environment_equals_default(self):
        """
        Checks whether location information corresponds to default location.
        """
        if self.save_window.scenario_time_of_day.currentText() == TimeOfDay.UNKNOWN.value and \
                self.save_window.scenario_weather.currentText() == Weather.UNKNOWN.value and \
                self.save_window.scenario_underground.currentText() == Underground.UNKNOWN.value and \
                self.save_window.scenario_time_hour.text() == "0" and self.save_window.scenario_time_minute.text() ==\
                "0":
            return True
        else:
            return False

    def location_equals_default(self):
        """
        Checks whether location information corresponds to default location.
        """
        if self.save_window.scenario_geo_anme_id.text() == "-999" and self.save_window.scenario_latitude.text() == \
                "999" and self.save_window.scenario_longitude.text() == "999" and self.environment_equals_default():
            return True
        else:
            return False

    def update_scenario_meta_data(self):
        if self.initialized:
            self.current_scenario.author = self.save_window.scenario_author.text()
            self.current_scenario.affiliation = self.save_window.scenario_affiliation.text()
            self.current_scenario.source = self.save_window.scenario_source.text()
            self.current_scenario.tags = [Tag(t) for t in self.save_window.scenario_tags.get_checked_items()]
            self.current_scenario.get_scenario_id().configuration_id = int(self.save_window.scenario_config_id.text())
            self.current_scenario.get_scenario_id().cooperative = self.save_window.cooperative_scenario.isChecked()
            self.current_scenario.get_scenario_id().country_id = self.save_window.country.currentText()
            self.current_scenario.get_scenario_id().map_id = int(self.save_window.scenario_scene_id.text())
            self.current_scenario.get_scenario_id().map_name = self.save_window.scenario_scene_name.text()
            self.current_scenario.get_scenario_id().obstacle_behavior = self.save_window.prediction_type.currentText()
            self.current_scenario.get_scenario_id().prediction_id = int(self.save_window.scenario_prediction_id.text())
            if self.location_equals_default() and self.current_scenario.location is None:
                self.current_scenario.location = None
            elif self.environment_equals_default() and not self.location_equals_default():
                self.current_scenario.location = Location(self.save_window.scenario_geo_anme_id.text(),
                                                          self.save_window.scenario_latitude.text(),
                                                          self.save_window.scenario_longitude.text())
            else:
                self.current_scenario.location = Location(self.save_window.scenario_geo_anme_id.text(),
                                                          self.save_window.scenario_latitude.text(),
                                                          self.save_window.scenario_longitude.text(),
                                                          )
                self.current_scenario.get_current_scenario().environment = \
                    Environment(Time(int(self.save_window.scenario_time_hour.text()),
                                int(self.save_window.scenario_time_minute.text())),
                                TimeOfDay(self.save_window.scenario_time_of_day.currentText()),
                                Weather(self.save_window.scenario_weather.currentText()),
                                Underground(self.save_window.scenario_underground.currentText()))

            self.save_window.label_benchmark_id.setText(str(self.current_scenario.get_scenario_id()))
