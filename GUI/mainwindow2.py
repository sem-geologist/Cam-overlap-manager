# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow2.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(908, 888)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralWidget)
        self.horizontalLayout.setContentsMargins(11, 11, 11, 11)
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralWidget)
        self.splitter.setLineWidth(1)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setHandleWidth(10)
        self.splitter.setObjectName("splitter")
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setLineWidth(1)
        self.frame.setObjectName("frame")
        self.availableOverlapsLayout = QtWidgets.QGridLayout(self.frame)
        self.availableOverlapsLayout.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.availableOverlapsLayout.setContentsMargins(1, 1, 1, 1)
        self.availableOverlapsLayout.setSpacing(6)
        self.availableOverlapsLayout.setObjectName("availableOverlapsLayout")
        self.minDateEdit = QtWidgets.QDateEdit(self.frame)
        self.minDateEdit.setDisplayFormat("dd-MM-yyyy")
        self.minDateEdit.setCalendarPopup(True)
        self.minDateEdit.setDate(QtCore.QDate(2014, 1, 1))
        self.minDateEdit.setObjectName("minDateEdit")
        self.availableOverlapsLayout.addWidget(self.minDateEdit, 1, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setMaximumSize(QtCore.QSize(16777215, 20))
        self.label_2.setObjectName("label_2")
        self.availableOverlapsLayout.addWidget(self.label_2, 1, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.availableOverlapsLayout.addItem(spacerItem, 1, 2, 1, 1)
        self.pet_button = QtWidgets.QToolButton(self.frame)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/pt.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pet_button.setIcon(icon)
        self.pet_button.setIconSize(QtCore.QSize(32, 32))
        self.pet_button.setObjectName("pet_button")
        self.availableOverlapsLayout.addWidget(self.pet_button, 1, 3, 1, 1)
        self.append_to_ofv_button = QtWidgets.QToolButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.append_to_ofv_button.sizePolicy().hasHeightForWidth())
        self.append_to_ofv_button.setSizePolicy(sizePolicy)
        self.append_to_ofv_button.setMinimumSize(QtCore.QSize(32, 50))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(True)
        font.setWeight(75)
        font.setKerning(False)
        self.append_to_ofv_button.setFont(font)
        self.append_to_ofv_button.setText("↲")
        self.append_to_ofv_button.setIconSize(QtCore.QSize(24, 31))
        self.append_to_ofv_button.setObjectName("append_to_ofv_button")
        self.availableOverlapsLayout.addWidget(self.append_to_ofv_button, 3, 3, 1, 1)
        self.sourceTV = QtWidgets.QTableView(self.frame)
        self.sourceTV.setMinimumSize(QtCore.QSize(300, 0))
        self.sourceTV.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.sourceTV.setTabKeyNavigation(False)
        self.sourceTV.setDragEnabled(True)
        self.sourceTV.setDragDropOverwriteMode(False)
        self.sourceTV.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.sourceTV.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.sourceTV.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.sourceTV.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.sourceTV.setShowGrid(False)
        self.sourceTV.setGridStyle(QtCore.Qt.NoPen)
        self.sourceTV.setSortingEnabled(True)
        self.sourceTV.setWordWrap(False)
        self.sourceTV.setCornerButtonEnabled(False)
        self.sourceTV.setObjectName("sourceTV")
        self.sourceTV.horizontalHeader().setCascadingSectionResizes(True)
        self.sourceTV.horizontalHeader().setDefaultSectionSize(50)
        self.sourceTV.horizontalHeader().setHighlightSections(False)
        self.sourceTV.horizontalHeader().setMinimumSectionSize(35)
        self.sourceTV.horizontalHeader().setSortIndicatorShown(False)
        self.sourceTV.verticalHeader().setVisible(False)
        self.sourceTV.verticalHeader().setDefaultSectionSize(20)
        self.sourceTV.verticalHeader().setHighlightSections(False)
        self.sourceTV.verticalHeader().setMinimumSectionSize(20)
        self.availableOverlapsLayout.addWidget(self.sourceTV, 3, 0, 1, 3)
        self.frame2 = QtWidgets.QFrame(self.splitter)
        self.frame2.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.frame2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame2.setObjectName("frame2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame2)
        self.gridLayout_2.setSizeConstraint(QtWidgets.QLayout.SetNoConstraint)
        self.gridLayout_2.setContentsMargins(1, 1, 1, 1)
        self.gridLayout_2.setSpacing(6)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.ovl_filename_label = QtWidgets.QLabel(self.frame2)
        self.ovl_filename_label.setObjectName("ovl_filename_label")
        self.gridLayout_2.addWidget(self.ovl_filename_label, 0, 1, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout_2.addItem(spacerItem1, 2, 2, 1, 1)
        self.delete_button = QtWidgets.QToolButton(self.frame2)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("icons/delete.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.delete_button.setIcon(icon1)
        self.delete_button.setIconSize(QtCore.QSize(32, 32))
        self.delete_button.setObjectName("delete_button")
        self.gridLayout_2.addWidget(self.delete_button, 3, 2, 1, 1)
        self.overlap_file_view = QtWidgets.QTableView(self.frame2)
        self.overlap_file_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.overlap_file_view.setTabKeyNavigation(False)
        self.overlap_file_view.setDragEnabled(True)
        self.overlap_file_view.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.overlap_file_view.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.overlap_file_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.overlap_file_view.setShowGrid(False)
        self.overlap_file_view.setGridStyle(QtCore.Qt.NoPen)
        self.overlap_file_view.setWordWrap(False)
        self.overlap_file_view.setCornerButtonEnabled(False)
        self.overlap_file_view.setObjectName("overlap_file_view")
        self.overlap_file_view.horizontalHeader().setCascadingSectionResizes(True)
        self.overlap_file_view.horizontalHeader().setDefaultSectionSize(50)
        self.overlap_file_view.horizontalHeader().setHighlightSections(False)
        self.overlap_file_view.horizontalHeader().setMinimumSectionSize(35)
        self.overlap_file_view.verticalHeader().setVisible(False)
        self.overlap_file_view.verticalHeader().setDefaultSectionSize(20)
        self.overlap_file_view.verticalHeader().setHighlightSections(False)
        self.overlap_file_view.verticalHeader().setMinimumSectionSize(20)
        self.gridLayout_2.addWidget(self.overlap_file_view, 1, 1, 3, 1)
        self.text_interface = QtWidgets.QPlainTextEdit(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.text_interface.sizePolicy().hasHeightForWidth())
        self.text_interface.setSizePolicy(sizePolicy)
        self.text_interface.setMinimumSize(QtCore.QSize(0, 80))
        self.text_interface.setMaximumSize(QtCore.QSize(16777215, 120))
        self.text_interface.setReadOnly(True)
        self.text_interface.setObjectName("text_interface")
        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 908, 32))
        self.menuBar.setObjectName("menuBar")
        self.menuFiles = QtWidgets.QMenu(self.menuBar)
        self.menuFiles.setObjectName("menuFiles")
        self.menuEdit = QtWidgets.QMenu(self.menuBar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtWidgets.QMenu(self.menuBar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setEnabled(True)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.RightToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)
        self.actionOpen_new_setup = QtWidgets.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("icons/load_new.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionOpen_new_setup.setIcon(icon2)
        self.actionOpen_new_setup.setObjectName("actionOpen_new_setup")
        self.actionSave_setup = QtWidgets.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("icons/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSave_setup.setIcon(icon3)
        self.actionSave_setup.setObjectName("actionSave_setup")
        self.actionRemove = QtWidgets.QAction(MainWindow)
        self.actionRemove.setIcon(icon1)
        self.actionRemove.setObjectName("actionRemove")
        self.actionAppend_to_down = QtWidgets.QAction(MainWindow)
        self.actionAppend_to_down.setObjectName("actionAppend_to_down")
        self.actionSettings = QtWidgets.QAction(MainWindow)
        self.actionSettings.setObjectName("actionSettings")
        self.actionAbout = QtWidgets.QAction(MainWindow)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout_Qt = QtWidgets.QAction(MainWindow)
        self.actionAbout_Qt.setObjectName("actionAbout_Qt")
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.menuFiles.addAction(self.actionOpen_new_setup)
        self.menuFiles.addAction(self.actionSave_setup)
        self.menuFiles.addSeparator()
        self.menuFiles.addAction(self.actionExit)
        self.menuEdit.addAction(self.actionRemove)
        self.menuEdit.addAction(self.actionAppend_to_down)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionSettings)
        self.menuHelp.addAction(self.actionAbout)
        self.menuHelp.addAction(self.actionAbout_Qt)
        self.menuBar.addAction(self.menuFiles.menuAction())
        self.menuBar.addAction(self.menuEdit.menuAction())
        self.menuBar.addAction(self.menuHelp.menuAction())
        self.mainToolBar.addAction(self.actionOpen_new_setup)
        self.mainToolBar.addAction(self.actionSave_setup)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.minDateEdit.setWhatsThis(_translate("MainWindow", "date filter with filters out overlap items with older than selection date"))
        self.label_2.setText(_translate("MainWindow", "filter by mod. date"))
        self.pet_button.setStatusTip(_translate("MainWindow", "show/hide element table (ctrl+T), overlap tree can be filtered by with element selection"))
        self.pet_button.setText(_translate("MainWindow", "..."))
        self.pet_button.setShortcut(_translate("MainWindow", "Ctrl+T"))
        self.append_to_ofv_button.setStatusTip(_translate("MainWindow", "append selection to the overlap file"))
        self.append_to_ofv_button.setWhatsThis(_translate("MainWindow", "button"))
        self.ovl_filename_label.setText(_translate("MainWindow", "New File:"))
        self.delete_button.setStatusTip(_translate("MainWindow", "delete the selected overlaps in the model"))
        self.delete_button.setText(_translate("MainWindow", "..."))
        self.text_interface.setPlainText(_translate("MainWindow", "The text message interface...."))
        self.menuFiles.setTitle(_translate("MainWindow", "Fi&les"))
        self.menuEdit.setTitle(_translate("MainWindow", "E&dit"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.mainToolBar.setAccessibleName(_translate("MainWindow", "main toolbar"))
        self.actionOpen_new_setup.setText(_translate("MainWindow", "&Open new setup"))
        self.actionOpen_new_setup.setToolTip(_translate("MainWindow", "Open existing or create the new overlap by pointing to valid setup file"))
        self.actionOpen_new_setup.setShortcut(_translate("MainWindow", "Ctrl+O"))
        self.actionSave_setup.setText(_translate("MainWindow", "&save overlap file"))
        self.actionSave_setup.setToolTip(_translate("MainWindow", "save the overlap model file"))
        self.actionSave_setup.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionRemove.setText(_translate("MainWindow", "&remove selected"))
        self.actionRemove.setShortcut(_translate("MainWindow", "Del"))
        self.actionAppend_to_down.setText(_translate("MainWindow", "&append selection to model bellow"))
        self.actionAppend_to_down.setToolTip(_translate("MainWindow", "append to overlap"))
        self.actionAppend_to_down.setShortcut(_translate("MainWindow", "Shift+Return"))
        self.actionSettings.setText(_translate("MainWindow", "&settings"))
        self.actionAbout.setText(_translate("MainWindow", "&About"))
        self.actionAbout_Qt.setText(_translate("MainWindow", "About &Qt"))
        self.actionExit.setText(_translate("MainWindow", "&exit"))
        self.actionExit.setShortcut(_translate("MainWindow", "Ctrl+X, Ctrl+Q"))
