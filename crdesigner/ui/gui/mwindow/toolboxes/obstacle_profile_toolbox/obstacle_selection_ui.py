from PyQt5 import QtCore, QtWidgets, QtGui

HEIGHT = 25
COLUMNS = 2
WIDTHF = 280
WIDTHM = 390
FACTOR = 0.7


class Obstacle_Selection_Ui(object):
    def __init__(self):
        self.selection = None
        self.mwindow = None

    def setupUI(self, selection, mwindow):
        self.mwindow = mwindow
        self.selection = selection
        self.selection.setObjectName("Obstacle Selection")
        self.selection.resize(1820 * FACTOR, 1150 * FACTOR)
        self.centralwidget = QtWidgets.QWidget(selection)
        self.centralwidget.setObjectName("centralwidget")
        self.centralLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.centralwidget.setObjectName("centralLayout")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.centralLayout.addWidget(self.tabWidget)
        self.tabBar = QtWidgets.QTabBar()
        self.tabWidget.setTabBar(self.tabBar)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frameLayout = QtWidgets.QHBoxLayout(self.frame)
        self.frame.setLayout(self.frameLayout)
        self.frame.setMaximumSize(int(1700 * FACTOR), 43)
        self.frame.setMinimumSize(int(1700 * FACTOR), 43)

        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frameLayout = QtWidgets.QHBoxLayout(self.frame)
        self.frame.setLayout(self.frameLayout)
        self.frame.setMaximumSize(int(1700 * FACTOR), 43)
        self.frame.setMinimumSize(int(1700 * FACTOR), 43)

        self.button_ok = QtWidgets.QPushButton(self.frame)
        self.button_ok.setObjectName("button_ok")
        self.button_ok.setMaximumSize(150, 40)

        self.button_cancel = QtWidgets.QPushButton(self.frame)
        self.button_cancel.setObjectName("button_cancel")
        self.button_cancel.setMaximumSize(150, 40)

        self.space = QtWidgets.QLabel()
        self.frameLayout.addWidget(self.space)
        self.frameLayout.addWidget(self.button_cancel)
        self.frameLayout.addWidget(self.button_ok)

        self.centralLayout.addWidget(self.frame)

        selection.setCentralWidget(self.centralwidget)

        self.update_window()
        self.retranslateUi(selection)
        QtCore.QMetaObject.connectSlotsByName(selection)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Obstacle Selection"))
        self.button_ok.setText(_translate("MainWindow", "Ok"))
        self.button_cancel.setText(_translate("MainWindow", "Cancel"))

    def update_window(self):
        p = QtGui.QPalette()
        p.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(self.mwindow.colorscheme()['background']))
        p.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(self.mwindow.colorscheme()['secondbackground']))
        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(self.mwindow.colorscheme()['background']))
        p.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(self.mwindow.colorscheme()['color']))
        p.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(self.mwindow.colorscheme()['color']))
        p.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(self.mwindow.colorscheme()['color']))
        p.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(self.mwindow.colorscheme()['background']))

        self.selection.setPalette(p)

        p.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(self.mwindow.colorscheme()['highlight']))
        p.setColor(QtGui.QPalette.ColorRole.Foreground, QtGui.QColor(self.mwindow.colorscheme()['highlighttext']))
        p.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(self.mwindow.colorscheme()['highlighttext']))
        self.tabBar.setPalette(p)
        self.button_ok.setPalette(p)

