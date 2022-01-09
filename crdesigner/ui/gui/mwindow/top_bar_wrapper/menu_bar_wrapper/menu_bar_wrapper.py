from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from crdesigner.ui.gui.mwindow.animated_viewer_wrapper.gui_sumo_simulation import SUMO_AVAILABLE
from crdesigner.ui.gui.mwindow.top_bar_wrapper.service_layer.general_services import create_action


class MenuBarWrapper:
    """
    Wrapper class for the menu bar.
    """

    def __init__(self, mwindow, file_new, open_commonroad_file, file_save, close_window, show_gui_settings,
                 show_sumo_settings, show_osm_settings, open_cr_web, open_cr_forum):
        self.menu_bar = mwindow.menuBar()  # instant of menu

        self.menu_file = self.menu_bar.addMenu('File')  # add menu 'file'
        # create new file
        self.action_new = create_action(mwindow=mwindow, text="New", icon=QIcon(":/icons/new_file.png"), checkable=False,
                                  slot=lambda: file_new(mwindow), tip="New Commonroad File", shortcut=QKeySequence.New)
        self.menu_file.addAction(self.action_new)
        # open a file
        self.action_open = create_action(mwindow=mwindow, text="Open", icon=QIcon(":/icons/open_file.png"), checkable=False,
                                   slot=lambda: open_commonroad_file(mwindow), tip="Open Commonroad File", shortcut=QKeySequence.Open)
        self.menu_file.addAction(self.action_open)
        # seperator
        self.separator = QAction(mwindow)
        self.separator.setSeparator(True)
        # safe a file
        self.action_save = create_action(mwindow=mwindow, text="Save", icon=QIcon(":/icons/save_file.png"), checkable=False,
                                   slot=lambda: file_save(mwindow), tip="Save Commonroad File", shortcut=QKeySequence.Save)
        self.menu_file.addAction(self.action_save)
        self.separator.setSeparator(True)
        # exit action
        self.exit_action = create_action(mwindow=mwindow, text="Quit", icon=QIcon(":/icons/close.png"), checkable=False,
                               slot=lambda: close_window(mwindow), tip="Quit", shortcut=QKeySequence.Close)
        self.menu_file.addAction(self.exit_action)

        self.menu_setting = self.menu_bar.addMenu('Setting')  # add menu 'Setting'
        self.gui_settings_action = create_action(mwindow=mwindow, text="GUI Settings", icon="", checkable=False,
                                 slot=lambda: show_gui_settings(mwindow), tip="Show settings for the CR Scenario Designer",
                                 shortcut=None)
        self.menu_setting.addAction(self.gui_settings_action)
        self.sumo_settings_action = None
        if SUMO_AVAILABLE:
            self.sumo_settings_action = create_action(mwindow=mwindow, text="SUMO Settings", icon="", checkable=False,
                                          slot=lambda: show_sumo_settings(mwindow), tip="Show settings for the SUMO interface",
                                          shortcut=None)
        self.menu_setting.addAction(self.sumo_settings_action)
        self.osm_settings_action = create_action(mwindow=mwindow, text="OSM Settings", icon="", checkable=False,
                                 slot=lambda: show_osm_settings(mwindow), tip="Show settings for osm converter", shortcut=None)
        self.menu_setting.addAction(self.osm_settings_action)

        self.menu_help = self.menu_bar.addMenu('Help')  # add menu 'Help'
        self.open_web_action = create_action(mwindow=mwindow, text="Open CR Web", icon="", checkable=False, slot=open_cr_web,
                             tip="Open CommonRoad Website", shortcut=None)
        self.menu_help.addAction(self.open_web_action)
        self.open_forum_action = create_action(mwindow=mwindow, text="Open Forum", icon="", checkable=False, slot=open_cr_forum,
                               tip="Open CommonRoad Forum", shortcut=None)
        self.menu_help.addAction(self.open_forum_action)
