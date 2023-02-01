from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QListWidget, QCheckBox

HEIGHT = 25
COLUMNS = 2
WIDTHF = 280
WIDTHM = 390
FACTOR = 0.7


class Obstacle_Selection_Ui(object):
    def __init__(self):
        self.selection = None
        self.mwindow = None
        self.selected_obstacles = [""]

    def setupUI(self, selection, mwindow):
        self.mwindow = mwindow
        self.selection = selection
        self.selection.setObjectName("Obstacle Selection")
        self.selection.resize(1000 * FACTOR, 1000 * FACTOR)
        self.centralwidget = QtWidgets.QWidget(selection)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralLayout.setObjectName("centralLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.centralLayout.addWidget(self.tabWidget)
        self.tabBar = QtWidgets.QTabBar()
        self.tabWidget.setTabBar(self.tabBar)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frameLayout = QtWidgets.QHBoxLayout(self.frame)
        self.frame.setLayout(self.frameLayout)
        self.frame.setMaximumSize(int(1000 * FACTOR), 43)
        self.frame.setMinimumSize(int(1000 * FACTOR), 43)

        self.button_ok = QtWidgets.QPushButton(self.frame)
        self.button_ok.setObjectName("button_ok")
        self.button_ok.setMaximumSize(150, 40)

        self.centralLayout.addWidget(self.frame)

        selection.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(selection)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 990, 23))
        self.menubar.setObjectName("menubar")
        selection.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(selection)
        self.statusbar.setObjectName("statusbar")
        selection.setStatusBar(self.statusbar)

        # add the obstacles
        self.gui_obstacles = self.ui_gui_obstacle(self.tabWidget)

        self.update_window()
        self.retranslateUi(selection)
        QtCore.QMetaObject.connectSlotsByName(selection)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Obstacle Selection"))
        self.button_ok.setText(_translate("MainWindow", "Ok"))

    def ui_gui_obstacle(self, tabWidget):
        self.scrollArea = QtWidgets.QScrollArea(tabWidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaLayout = QtWidgets.QGridLayout(self.scrollArea)

        self.contentWrapper = QtWidgets.QWidget()
        self.contentWrapper.setObjectName("ContentWrapper")
        self.HBoxLayout = QtWidgets.QHBoxLayout(self.contentWrapper)
        self.HBoxLayout.setObjectName("gridLayout")
        self.HBoxLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.HBoxLayout.setAlignment(QtCore.Qt.AlignTop)

        self.content = QtWidgets.QWidget(self.contentWrapper)
        self.content.setObjectName("scrollAreaWidgetContents")
        self.formLayout = QtWidgets.QFormLayout(self.content)
        self.formLayout.setObjectName("form")
        self.content.setMinimumSize(860 * FACTOR, 820)
        self.content.setLayout(self.formLayout)
        self.HBoxLayout.addWidget(self.content)

        if self.selected_obstacles not in ["", "None"]:
            for obstacle in self.selected_obstacles:
                self.checkbox = QCheckBox(self.content)
                self.checkbox.setText("Obstacle: " + str(obstacle))
                self.checkbox.setObjectName(str(obstacle))
                self.HBoxLayout.addWidget(self.checkbox)
                self.formLayout.addRow(self.checkbox)

        self.scrollArea.setWidget(self.contentWrapper)

        self.tabWidget.addTab(self.scrollArea, "Obstacles")

    def update_window(self):
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(self.mwindow.colorscheme().background))
        p.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(self.mwindow.colorscheme().second_background))
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(self.mwindow.colorscheme().background))
        p.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(self.mwindow.colorscheme().color))
        p.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(self.mwindow.colorscheme().color))
        p.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(self.mwindow.colorscheme().color))
        p.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(self.mwindow.colorscheme().background))

        self.selection.setPalette(p)

        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(self.mwindow.colorscheme().highlight))
        p.setColor(QtGui.QPalette.ColorRole.Foreground, QtGui.QColor(self.mwindow.colorscheme().highlight_text))
        p.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(self.mwindow.colorscheme().highlight_text))
        self.button_ok.setPalette(p)
