from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import QListWidget, QCheckBox, QMainWindow

HEIGHT = 25
COLUMNS = 2
WIDTHF = 280
WIDTHM = 390
FACTOR = 0.7


class Obstacle_Selection_Ui(object):
    def __init__(self, mwindow):
        self.selection = QMainWindow()
        self.mwindow = mwindow
        self.scenario_obstacles = []
        self.setupUI()

    def setupUI(self):
        self.selection.setObjectName("Obstacle Selection")
        self.selection.resize(1000 * FACTOR, 1000 * FACTOR)
        self.centralwidget = QtWidgets.QWidget(self.selection)
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

        self.selection.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self.selection)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 990, 23))
        self.menubar.setObjectName("menubar")
        self.selection.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self.selection)
        self.statusbar.setObjectName("statusbar")
        self.selection.setStatusBar(self.statusbar)

        self.ui_gui_obstacle(self.tabWidget)
        self.update_window()
        self.retranslateUi(self.selection)
        QtCore.QMetaObject.connectSlotsByName(self.selection)

    def showSelection(self):
        self.selection.show()

    def closeSelection(self):
        self.selection.close()

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

        for obstacle in self.scenario_obstacles:
            checkbox = QCheckBox(self.content)
            checkbox.setText(str(obstacle))
            checkbox.setObjectName(str(obstacle))
            self.HBoxLayout.addWidget(checkbox)
            self.formLayout.addRow(checkbox)

        self.scrollArea.setWidget(self.contentWrapper)

        self.tabWidget.addTab(self.scrollArea, "Obstacles")

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Obstacle self.Selection"))
        self.button_ok.setText(_translate("MainWindow", "Ok"))

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
