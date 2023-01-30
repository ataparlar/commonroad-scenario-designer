from PyQt5.QtWidgets import QMainWindow

from crdesigner.ui.gui.mwindow.toolboxes.obstacle_profile_toolbox.obstacle_selection_ui import Obstacle_Selection_Ui
from crdesigner.ui.gui.mwindow.animated_viewer_wrapper.commonroad_viewer.dynamic_canvas import DynamicCanvas
import crdesigner.ui.gui.mwindow.service_layer.sumo_settings as sumo
from crdesigner.ui.gui.mwindow.animated_viewer_wrapper.gui_sumo_simulation import SUMO_AVAILABLE


class Obstacle_Selection:
    def __init__(self, parent):
        self.cr_designer = parent
        self.obstacle_selection_window = QMainWindow()
        self.window = Obstacle_Selection_Ui()

        self.window.setupUI(self.obstacle_selection_window, self.cr_designer)
        self.connect_events()
        self.obstacle_selection_window.show()
        self.canvas = DynamicCanvas()

    def connect_events(self):
        """ connect buttons to callables """
        self.window.button_cancel.clicked.connect(self.close)
        if SUMO_AVAILABLE:
            self.sumo_settings.connect_events()

    def close(self):
        self.obstacle_selection_window.close()