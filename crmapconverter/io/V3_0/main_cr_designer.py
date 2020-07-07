import signal
import sys
import os
from lxml import etree
import numpy as np
import matplotlib.pyplot as plt
import time

from crmapconverter.io.V3_0.GUI_resources.MainWindow import Ui_mainWindow
from crmapconverter.io.V3_0.gui_toolbox import UpperToolbox, AnimationTool
from crmapconverter.io.V3_0.gui_sumo_simulation import AnimationPlay, AnimationStepPlay
from crmapconverter.io.V3_0.gui_cr_viewer import CrViewer
from crmapconverter.io.V3_0.gui_opendrive2cr import OD2CR
from crmapconverter.io.V3_0.gui_osm2cr import OSM2CR
from crmapconverter.io.V3_0.gui_setting_interface import Setting
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


from commonroad.common.file_writer import CommonRoadFileWriter

from crmapconverter.io.V3_0.GUI_src import CR_Scenario_Designer


class MWindow(QMainWindow, Ui_mainWindow):
    """The Mainwindow of CR Scenario Designer."""

    count = 0
    tool1 = None
    tool2 = None
    toolBox = None
    console = None
    textBrowser = None
    sumobox = None
    play = None
    crviewer = None
    lanelets_List = None
    play_step = None
    timer = None
    ani_path = None
    od2cr = None

    def __init__(self):
        super(MWindow, self).__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon(':/icons/cr.ico'))
        self.centralwidget.setStyleSheet('background-color:rgb(150,150,150)')
        self.setWindowFlag(True)

        self.current_scenario = None
        self.commoroad_filename = None
        self.selected_lanelet_id = None

        self.create_file_actions()
        self.create_import_actions()
        self.create_export_actions()
        self.create_setting_actions()
        self.create_toolbar()
        self.create_console()
        self.create_toolbox()

        self.status = self.statusbar
        self.status.showMessage("Welcome to CR Scenario Designer")

        menuBar = self.menuBar()  # instant of menu
        file = menuBar.addMenu('File')  # add menu 'file'

        file.addAction(self.fileNewAction)
        file.addAction(self.fileOpenAction)
        file.addAction(self.fileSaveAction)
        file.addAction(self.separator)
        file.addAction(self.exitAction)

        menu_import = menuBar.addMenu('Import')  # add menu 'Import'
        menu_import.addAction(self.importfromOpendrive)
        menu_import.addAction(self.importfromOSM)
        # menu_import.addAction(self.importfromSUMO)

        menu_export = menuBar.addMenu('Export')  # add menu 'Export'
        menu_export.addAction(self.exportAsCommonRoad)
        # menu_export.addAction(self.exportAsOSM)
        # menu_export.addAction(self.export2SUMO)

        menu_setting = menuBar.addMenu('Setting')  # add menu 'Setting'
        menu_setting.addAction(self.setting)

        self.center()

    def setting_interface(self):
        self.set = Setting()

    def create_toolbox(self):
        """ Create the Upper toolbox."""
        self.uppertoolBox = UpperToolbox()

        self.tool1 = QDockWidget("ToolBox")
        self.tool1.setFloating(True)
        self.tool1.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.tool1.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.tool1.setWidget(self.uppertoolBox)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool1)
        self.create_sumobox()
        self.uppertoolBox.button_sumo_simulation.clicked.connect(
            self.tool_box2_show)
        self.uppertoolBox.button_lanlist.clicked.connect(self.show_laneletslist)

    def create_laneletslist(self, object):
        """Create the Laneletslist and put it into right Dockwidget area."""
        if self.lanelets_List is not None:
            self.lanelets_List.close()
            self.lanelets_List = None
        self.lanelets_List = QDockWidget(
            "Lanelets list " + object.filename)
        self.lanelets_List.setFloating(True)
        self.lanelets_List.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.lanelets_List.setAllowedAreas(Qt.RightDockWidgetArea)
        self.lanelets_List.setWidget(object.laneletsList)
        self.addDockWidget(Qt.RightDockWidgetArea, self.lanelets_List)

    def show_laneletslist(self):
        """Function connected with button 'Lanelets List' to show the lanelets list."""
        if self.crviewer is None:
            if self.od2cr is None:
                messbox = QMessageBox()
                reply = messbox.question(
                    self,
                    "Warning",
                    "Please load or convert a CR Scenario or first",
                    QtWidgets.QMessageBox.Ok)
                if (reply == QtWidgets.QMessageBox.Ok):
                    messbox.close()
                else:
                    messbox.close()
            else:self.lanelets_List.show()
        else:
            self.lanelets_List.show()

    def create_sumobox(self):
        """Function to create the sumo toolbox(bottom toolbox)."""
        self.sumobox = AnimationTool()
        self.tool2 = QDockWidget("Sumo Simulation", self)
        self.tool2.setFeatures(QDockWidget.AllDockWidgetFeatures)
        self.tool2.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.tool2.setWidget(self.sumobox)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tool2)
        self.tool2.setMinimumHeight(400)
        self.sumobox.button_import.clicked.connect(lambda:self.import_animation(None))
        self.sumobox.button_save.clicked.connect(self.save_animation)
        self.sumobox.button_pause.clicked.connect(self.pause_animation)
        self.sumobox.button_play.clicked.connect(self.play_animation)

        """for sumo frame by frame play"""
        self.sumobox.slider.valueChanged[int].connect(self.timestep_change)

    def activate_sumoanimation_step(self):
        if self.lanelets_List is not None:
            self.lanelets_List.close()
            self.lanelets_List = None
        if self.play is not None:
            self.play.ani.event_source.stop()
        if self.ani_path != None:
            self.textBrowser.append("Showing Simulation frame by frame")
            self.play_step = AnimationStepPlay(self.ani_path)
        if self.play_step.commonroad_filename is not None:
            # play.current_scenario = scenario_editing.current_scenario
            self.play_step.setWindowIcon(QIcon(":/icons/cr1.ico"))
            self.setCentralWidget(self.play_step)
            self.commoroad_filename = self.play_step.commonroad_filename
            self.play_step.play_timesteps(self.play_step.current_scenario, 0)
            self.textBrowser.append("Ready")

    def timestep_change(self, value):
        if self.play is not None:
            if self.play_step is None:
                self.activate_sumoanimation_step()
            if self.sumobox.radioButton.isChecked():
                # self.sumobox.slider.setValue(value)
                self.sumobox.label.setText('Timestep: ' + str(value))
                self.play_step.play_timesteps(
                    self.play_step.current_scenario, value)

    def play_animation(self):
        """Function connected with the play button in the sumo-toolbox."""
        if self.play is not None:
            if self.play_step is not None:
                self.sumobox.radioButton.setChecked(False)
                self.import_animation(self.ani_path)
                self.play.ani.event_source.start()
                self.play_step = None
            else:
                self.play.ani.event_source.start()
        else:
            messbox = QMessageBox()
            reply = messbox.question(
                self,
                "Warning",
                "You should firstly load an animation",
                QMessageBox.Ok | QMessageBox.No,
                QMessageBox.Ok)
            if (reply == QtWidgets.QMessageBox.Ok):
                self.play_animation()
            else:
                messbox.close()

    def pause_animation(self):
        """Function connected with the pause button in the sumo-toolbox."""
        if self.play is not None:
            self.play.ani.event_source.stop()
        else:
            messbox = QMessageBox()
            reply = messbox.question(
                self,
                "Warning",
                "You should firstly load an animation",
                QMessageBox.Ok | QMessageBox.No,
                QMessageBox.Ok)
            if (reply == QtWidgets.QMessageBox.Ok):
                self.play_animation()
            else:
                messbox.close()

    def import_animation(self, path):
        """Function connected with the pause button in the sumo-toolbox."""
        if self.lanelets_List is not None:
            self.lanelets_List.close()
            self.lanelets_List = None
        if self.play is not None:
            self.play.ani.event_source.stop()

        self.textBrowser.append("Opening the CR Scenario Simulation")
        self.play = AnimationPlay(path)
        if self.play.commonroad_filename is not None:
            # play.current_scenario = scenario_editing.current_scenario
            self.ani_path = self.play.path
            self.play.setWindowIcon(QIcon(":/icons/cr1.ico"))
            self.setCentralWidget(self.play)
            self.play.setWindowFlags(Qt.WindowCloseButtonHint)
            self.commoroad_filename = self.play.commonroad_filename
            # window.setWindowTitle(scenario_editing.commonroad_filename)  # set up
            # the title

    # self.textBrowser.append("loading Animation " + scenario_editing.commonroad_filename)
    # self.status.showMessage("Opening " + crviewer.commonroad_filename)

    def save_animation(self):
        """Function connected with the save button in the sumo-toolbox."""
        if self.play is None:
            messbox = QMessageBox()
            reply = messbox.question(
                self,
                "Warning",
                "You should firstly load an animation",
                QMessageBox.Ok | QMessageBox.No,
                QMessageBox.Ok)
            if (reply == QtWidgets.QMessageBox.Ok):
                self.import_animation()
            else:
                messbox.close()
        else:
            self.play.save_animation(self.sumobox.save_menu.currentText())

    def create_console(self):
        """Function to create the console."""
        self.console = QDockWidget(self)
        self.console.setTitleBarWidget(
            QWidget(self.console))  # no title of Dock
        self.textBrowser = QtWidgets.QTextBrowser()
        self.textBrowser.setMaximumHeight(80)
        self.textBrowser.setObjectName("textBrowser")
        self.console.setWidget(self.textBrowser)
        self.console.setFloating(False)  # set if console can float
        self.console.setFeatures(QDockWidget.NoDockWidgetFeatures)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console)

    def create_toolbar(self):
        """Function to create toolbar of the main Window."""
        tb1 = self.addToolBar("File")
        new = QAction(QIcon(":/icons/new_file.png"), "new CR File", self)
        tb1.addAction(new)
        new.triggered.connect(self.file_new)
        open = QAction(QIcon(":/icons/open_file.png"), "open CR File", self)
        tb1.addAction(open)
        open.triggered.connect(self.file_open)
        save = QAction(QIcon(":/icons/save_file.png"), "save CR File", self)
        tb1.addAction(save)
        save.triggered.connect(self.file_save)
        tb1.addSeparator()
        tb2 = self.addToolBar("ToolBox")
        toolbox = QAction(
            QIcon(":/icons/tools.ico"),
            "show Toolbox for CR Scenario",
            self)
        tb2.addAction(toolbox)
        toolbox.triggered.connect(self.tool_box1_show)
        tb2.addSeparator()
        tb3 = self.addToolBar("Animation Play")
        self.button_play = QAction(
            QIcon(":/icons/play.png"),
            "Play and Pause the animation",
            self)
        tb3.addAction(self.button_play)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMaximumWidth(300)
        self.slider.setValue(0)
        self.slider.setMinimum(0)
        self.slider.setMaximum(99)
        #self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)
        self.slider.setToolTip(
            "Show corresponding Scenario at selected timestep")
        tb3.addWidget(self.slider)

        self.label = QLabel('Step: 0', self)
        tb3.addWidget(self.label)

    def create_import_actions(self):
        """Function to create the import action in the menu bar."""
        self.importfromOpendrive = self.create_action(
            "From OpenDrive",
            icon="",
            checkable=False,
            slot=self.opendrive_2_cr,
            tip="Convert from OpenDrive to CommonRoad",
            shortcut=None)
        self.importfromOSM = self.create_action(
            "From OSM",
            icon="",
            checkable=False,
            slot=self.osm_2_cr,
            tip="Convert from OSM to CommonRoad",
            shortcut=None)

    def opendrive_2_cr(self):
        """Function to realize converter OD2CR and show the result."""
        self.od2cr = OD2CR()
        self.od2cr.setWindowIcon(QIcon(":/icons/Groupe_3.ico"))
        if self.od2cr.filename is not None:
            self.setCentralWidget(self.od2cr)  # setup mdi of CR File
            self.setWindowTitle(self.od2cr.filename)  # set up the title
            self.create_laneletslist(self.od2cr)
            self.textBrowser.append("Converted from " + self.od2cr.filename)
            self.textBrowser.append(self.od2cr.statsText)
            self.textBrowser.setMaximumHeight(800)

        else:
            self.textBrowser.append(
                "Terminated because no OpenDrive file selected")

    def osm_2_cr(self):
        """Function to realize converter OSM2CR and show the result."""
        # window = QMdiSubWindow()  #
        osm2cr = OSM2CR()

    def create_export_actions(self):
        """Function to create the export action in the menu bar."""
        self.exportAsCommonRoad = self.create_action(
            "As CommonRoad",
            icon="",
            checkable=False,
            slot=self.file_save,
            tip="Save as CommonRoad File (the same function as Save)",
            shortcut=None)
        self.exportAsOSM = self.create_action(
            "From OSM",
            icon="",
            checkable=False,
            slot=self.osm_2_cr,
            tip="Convert from OSM to CommonRoad",
            shortcut=None)

    def create_setting_actions(self):
        """Function to create the export action in the menu bar."""
        self.setting = self.create_action(
            "Settings",
            icon="",
            checkable=False,
            slot=self.setting_interface,
            tip="Show settings for converters",
            shortcut=None)

    def center(self):
        """Function that makes sure the main window is in the center of screen."""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2)

    def create_file_actions(self):
        """Function to create the file action in the menu bar."""
        self.fileNewAction = self.create_action(
            "New",
            icon=QIcon(":/icons/new_file.png"),
            checkable=False,
            slot=self.file_new,
            tip="New Commonroad File",
            shortcut=QKeySequence.New)
        self.fileOpenAction = self.create_action(
            "Open",
            icon=QIcon(":/icons/open_file.png"),
            checkable=False,
            slot=self.file_open,
            tip="Open Commonroad File",
            shortcut=QKeySequence.Open)
        self.separator = QAction(self)
        self.separator.setSeparator(True)

        self.fileSaveAction = self.create_action(
            "Save",
            icon=QIcon(":/icons/save_file.png"),
            checkable=False,
            slot=self.file_save,
            tip="Save Commonroad File",
            shortcut=QKeySequence.Save)
        self.separator.setSeparator(True)
        self.exitAction = self.create_action(
            "Quit",
            icon=QIcon(":/icons/close.png"),
            checkable=False,
            slot=self.close_window,
            tip="Quit",
            shortcut=QKeySequence.Close)

    def create_action(
            self,
            text,
            icon=None,
            checkable=False,
            slot=None,
            tip=None,
            shortcut=None):
        """Function to create the action in the menu bar."""
        action = QAction(text, self)
        if icon is not None:
            action.setIcon(QIcon(icon))
        if checkable:
            # toggle, True means on/off state, False means simply executed
            action.setCheckable(True)
            if slot is not None:
                action.toggled.connect(slot)
        else:
            if slot is not None:
                action.triggered.connect(slot)
        if tip is not None:
            action.setToolTip(tip)  # toolbar tip
            action.setStatusTip(tip)  # statusbar tip
        if shortcut is not None:
            action.setShortcut(shortcut)  # shortcut
        return action

    def file_new(self):
        """Function to create the action in the menu bar."""
        """Not Finished---"""
        new = QTextEdit()
        new.setWindowTitle("New")
        new.setWindowIcon(QIcon(":/icons/cr.ico"))
        self.setCentralWidget(QTextEdit())  # setup new scenario file
        self.textBrowser.append("add new file")
        # show message in statusbar
        self.status.showMessage("Creating New File")

    def file_open(self):
        """Function to open a CR .xml file."""
        if self.play is not None:
            self.play.ani._stop()

        self.crviewer = CrViewer()
        self.crviewer.setWindowIcon(QIcon(":/icons/cr1.ico"))
        if self.crviewer.filename is not None:
            self.create_laneletslist(self.crviewer)
            # window.setWindowTitle(self.crviewer.commonroad_filename)  # set
            # up the title
            self.textBrowser.append(
                "loading " + self.crviewer.filename)
            # self.status.showMessage("Opening " + crviewer.commonroad_filename)
            self.setCentralWidget(self.crviewer)
            self.commoroad_filename = self.crviewer.filename
        else:
            self.textBrowser.append(
                "Terminated because no CommonRoad file selected")

    def file_save(self):
        """Function to save a CR .xml file."""
        fileEdit = self.centralWidget()
        if fileEdit is None:
            messbox = QMessageBox()
            reply = messbox.warning(
                self,
                "Warning",
                "There is no file to save!",
                QMessageBox.Ok,
                QMessageBox.Ok)

            if reply == QMessageBox.Ok:
                messbox.close()
            else:
                messbox.close()

        else:
            # if self.commonroad_filename == "":

            if not fileEdit.current_scenario:
                return
            path, _ = QFileDialog.getSaveFileName(
                self,
                "QFileDialog.getSaveFileName()",
                ".xml",
                "CommonRoad files *.xml (*.xml)",
                options=QFileDialog.Options(),
            )

            if not path:
                self.no_file_named()
                return

            try:
                with open(path, "w") as fh:
                    writer = CommonRoadFileWriter(
                        scenario=fileEdit.current_scenario,
                        planning_problem_set=None,
                        author="",
                        affiliation="",
                        source="",
                        tags="",
                    )
                    writer.write_scenario_to_file(path)
            except (IOError) as e:
                QMessageBox.critical(
                    self,
                    "CommonRoad file not created!",
                    "The CommonRoad file was not saved due to an error.\n\n{}".format(e),
                    QMessageBox.Ok,
                )
                return

    def processtrigger(self, q):
        self.status.showMessage(q.text() + ' is triggered')

    def close_window(self):
        reply = QMessageBox.warning(
            self,
            "Warning",
            "Do you really want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes)
        if reply == QMessageBox.Yes:
            qApp.quit()

    def closeEvent(self, event):
        result = QtWidgets.QMessageBox.question(
            self,
            "Warning",
            "Do you want to exit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if (result == QtWidgets.QMessageBox.Yes):
            event.accept()
        else:
            event.ignore()

    def tool_box1_show(self):
        self.tool1.show()

    def tool_box2_show(self):
        self.tool2.show()

    def no_file_named(self):
        messbox = QMessageBox()
        reply = messbox.warning(
            self,
            "Warning",
            "You should name the file!",
            QMessageBox.Ok | QMessageBox.No,
            QMessageBox.Ok)

        if reply == QMessageBox.Ok:
            self.file_save()
        else:
            messbox.close()


if __name__ == '__main__':
    # application
    app = QApplication(sys.argv)
    w = MWindow()
    w.show()
    sys.exit(app.exec_())
