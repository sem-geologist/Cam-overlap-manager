# -*- coding: utf-8 -*-
#
# Copyright 2016 Petras Jokubauskas
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with any project and source this library is coupled.
# If not, see <http://www.gnu.org/licenses/>.
#

from PyQt5 import QtCore, Qt
import re

#the periodic table possitions in gui:
# row, column:
pt_indexes = {'H': (0, 0), 'He': (0, 17), 'Li': (1, 0),
              'Be': (1, 1), 'B': (1, 12), 'C': (1, 13),
              'N': (1, 14), 'O': (1, 15), 'F': (1, 16),
              'Ne': (1, 17), 'Na': (2, 0), 'Mg': (2, 1),
              'Al': (2, 12), 'Si': (2, 13), 'P': (2, 14),
              'S': (2, 15), 'Cl': (2, 16), 'Ar': (2, 17),
              'K': (3, 0), 'Ca': (3, 1), 'Sc': (3, 2),
              'Ti': (3, 3), 'V': (3, 4), 'Cr': (3, 5),
              'Mn': (3, 6), 'Fe': (3, 7), 'Co': (3, 8),
              'Ni': (3, 9), 'Cu': (3, 10), 'Zn': (3, 11),
              'Ga': (3, 12), 'Ge': (3, 13), 'As': (3, 14),
              'Se': (3, 15), 'Br': (3, 16), 'Kr': (3, 17),
              'Rb': (4, 0), 'Sr': (4, 1), 'Y': (4, 2),
              'Zr': (4, 3), 'Nb': (4, 4), 'Mo': (4, 5),
              'Tc': (4, 6), 'Ru': (4, 7), 'Rh': (4, 8),
              'Pd': (4, 9), 'Ag': (4, 10), 'Cd': (4, 11),
              'In': (4, 12), 'Sn': (4, 13), 'Sb': (4, 14),
              'Te': (4, 15), 'I': (4, 16), 'Xe': (4, 17),
              'Cs': (5, 0), 'Ba': (5, 1), 'La': (7, 3),
              'Ce': (7, 4), 'Pr': (7, 5), 'Nd': (7, 6),
              'Pm': (7, 7), 'Sm': (7, 8), 'Eu': (7, 9),
              'Gd': (7, 10), 'Tb': (7, 11), 'Dy': (7, 12),
              'Ho': (7, 13), 'Er': (7, 14), 'Tm': (7, 15),
              'Yb': (7, 16), 'Lu': (7, 17), 'Hf': (5, 3),
              'Ta': (5, 4), 'W': (5, 5), 'Re': (5, 6),
              'Os': (5, 7), 'Ir': (5, 8), 'Pt': (5, 9),
              'Au': (5, 10), 'Hg': (5, 11), 'Tl': (5, 12),
              'Pb': (5, 13), 'Bi': (5, 14), 'Po': (5, 15),
              'At': (5, 16), 'Rn': (5, 17), 'Fr': (6, 0),
              'Ra': (6, 1), 'Ac': (8, 3), 'Th': (8, 4),
              'Pa': (8, 5), 'U': (8, 6), 'Np': (8, 7),
              'Pu': (8, 8)}

#element groups:
#TODO: this could go to json and configs
geo_groups = {'LITHOPHILE': ['Na', 'K', 'Rb', 'Cs', 'Sc', 'Si', 'Al', 'Ti', 'Mg', 'Ca'],
              'SIDEROPHILE': ['Fe', 'Co', 'Ni', 'Pt', 'Re', 'Os'],
              'CHALCOPHILE': ['Cu', 'Ag', 'Zn', 'Pb', 'S', 'As'],
              'LILE': ['K', 'Rb', 'Cs', 'Ba'],
              'HFSE': ['Zr', 'Nb', 'Th', 'U'],
              'MAJOR': ['O', 'Na', 'K', 'Si', 'Al', 'Ti', 'Mg',
                        'Ca', 'Fe'],
              'HALOGENS': ['F', 'Cl', 'Br'],
              'REE': ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm',
                      'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er',
                      'Tm', 'Yb', 'Lu'],
              'LREE': ['La', 'Ce', 'Pr', 'Nd', 'Pm', 'Sm'],
              'HREE': ['Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er',
                      'Tm', 'Yb', 'Lu'],
              'COMMON': ['O', 'Na', 'K', 'Si', 'Al', 'Ti', 'Mg', 'Ca',
                            'Cr', 'Mn', 'Fe'],
			  'NOBLE': ['Ru', 'Rh', 'Pd', 'Os', 'Ir', 'Pt', 'Au'],
              'ALL': ['He', 'Se', 'Sb', 'Pt', 'Ar', 'Ba', 'As', 'Pa',
                      'Au', 'Dy', 'Bi', 'U', 'Ne', 'Re', 'Al', 'Sc',
                      'Mn', 'Ra', 'In', 'O', 'P', 'Mo', 'Tb', 'V',
                      'Na', 'Ta', 'Hg', 'Ca', 'Hf', 'Ac', 'Eu', 'Nd',
                      'Br', 'Ag', 'Kr', 'W', 'K', 'S', 'Ga', 'At',
                      'Co', 'Sr', 'C', 'Ce', 'Be', 'I', 'Ni', 'Er',
                      'Cu', 'Cr', 'Ho', 'B', 'Li', 'Nb', 'Ru', 'Si',
                      'H', 'Rn', 'Zn', 'Yb', 'Pm', 'Te', 'Ti', 'F',
                      'Pu', 'Lu', 'La', 'Ge', 'Ir', 'Mg', 'Po', 'Pd',
                      'Y', 'Sn', 'Sm', 'Np', 'Zr', 'Cl', 'Tl', 'Xe',
                      'Gd', 'Os', 'Fe', 'Pb', 'Tm', 'Cd', 'N', 'Tc',
                      'Cs', 'Pr', 'Th', 'Rb', 'Fr', 'Rh']}

element_regex = r"C[laroudse]?|Os?|N[eaibdps]?|S[icernbm]?|"\
        r"H[eofga]?|A[lrsgutcm]|B[erai]?|Dy|E[ur]|F[er]?|G[aed]|"\
        r"I[nr]?|Kr?|L[iau]|M[gno]|R[buhena]|T[icebmalh]|"\
        r"U|V|W|Xe|Yb?|Z[nr]|P[drmtboau]?"

geo_regex = '(?:%s)' % '|'.join(geo_groups.keys())


class HoverableButton(Qt.QPushButton):

    def __init__(self, name):
        Qt.QAbstractButton.__init__(self)
        self.setMouseTracking(1)
        self.setText(name)
        self.setCheckable(True)
        self.hoverState = False
        self.orig_size = self.geometry()
        self.pal = self.palette()

    def enterEvent(self, event):
        if self.isEnabled():
            self.hoverState = True
            self.orig_size = self.geometry()
            #some fancy graphic effects (inspired by KDE kalzium):
            self.setGeometry(self.orig_size.x() - self.orig_size.width() / 5,
                             self.orig_size.y() - self.orig_size.height() / 5,
                             self.orig_size.width() * 1.4,
                             self.orig_size.height() * 1.4)
            self.raise_()

    def leaveEvent(self, event):
        if self.isEnabled():
            self.hoverState = False
            self.setGeometry(self.orig_size)


class ElementTableGUI(Qt.QTableWidget):
    """
    Create the periodic element gui with toggleble buttons
    for element selection and preview signal triggered with
    mouse hover events.
    Initialisation can take python list with elements
    for which buttons is pretoggled:
    -----------
    args:
    preenabled -- python list with elements (abbrevations)
    -----------
    instantiates:
    QtGui.QTableWidget object with additional signals:
    enableElementPrev -- signal with element name which
       button were hovered
    disableElementPrev -- singal with element name emit
       after mouse leaves button area
    enableElement -- mapped toggle signal of button emitting
       name of element
    disableElement -- mapped toggle signal of button emitting
       name of element
    """
    # button press slots:
    enableElement = QtCore.pyqtSignal(str)
    disableElement = QtCore.pyqtSignal(str)
    allElementsOff = QtCore.pyqtSignal()

    def __init__(self, parent=None, preenabled=[]):
        Qt.QTableWidget.__init__(self, parent)
        self.setWindowTitle('Element Table')
        self.setColumnCount(18)
        self.setRowCount(9)
        self.horizontalHeader().setSectionResizeMode(Qt.QHeaderView.Stretch)
        self.verticalHeader().setSectionResizeMode(Qt.QHeaderView.Stretch)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self._populate_table(preenabled)
        self.setSpan(6, 3, 1, 15)  # for decorative line
        self.setSpan(8, 9, 1, 9)  # for text input widget
        self.setSpan(7, 0, 2, 3)  # for Clear All button
        #self.setSpan(8, 0, 1, 3)  # for overlap option
        self._setup_text_interface()
        self._setup_etc()
        self.resize(550, 300)

    def _setup_etc(self):
        self.setShowGrid(False)
        self.setEditTriggers(Qt.QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(Qt.QAbstractItemView.NoSelection)
        self.clearButton = Qt.QPushButton('Clear All')
        #self.preview = Qt.QTableWidgetItem('preview')
        self.setCellWidget(7, 0, self.clearButton)
        self.clearButton.setStyleSheet("""font: bold;""")
        self.clearButton.pressed.connect(self.clear_all)
        #self.previewCheck = self.item(7, 0)
        #self.previewCheck.setCheckState(QtCore.Qt.Checked)

    def _setup_text_interface(self):
        self.textInterface = Qt.QLineEdit()
        self.setCellWidget(8, 9, self.textInterface)
        self.textInterface.returnPressed.connect(self.parseText)
        self.textInterface.setToolTip(
"""
text interface:
You can write abbrevations of elements:
without any space:
    AlSiNaK
with any separators like comma/space:
    Al;Br K,La
abbrevations of element groups:
    HFSE, REE, REE_SEM, LILE, mAjor
Use '-' (minus) sign to switch all elements after it:
    -AlCa, K; P -> toggles off Al, Ca, K, P
    HFSE - Nb -> toggles on HFSE elements, but switches off Nb
""")
        completer = Qt.QCompleter(list(pt_indexes.keys()) +
                                     list(geo_groups.keys()))
        self.textInterface.setCompleter(completer)

    def parseText(self):
        ptext = str(self.textInterface.text())
        if '-' in ptext:
            first_level = re.findall(r"[-]|[A-Z a-z,;]*", ptext)
            if first_level.index('-') == 0:
                positive_text = ''
                negative_text = first_level[1]
            else:
                positive_text = first_level[0]
                negative_text = first_level[first_level.index('-') + 1]
        else:
            positive_text = ptext
            negative_text = ''
        # clear text interface:
        self.textInterface.clear()
        # parse what to add first:
        parsed = []
        geo_list = re.findall(geo_regex, positive_text)
        for i in geo_list:
            parsed.extend(geo_groups[i])
            positive_text = positive_text.replace(i, '')
        parsed.extend(re.findall(element_regex, positive_text))
        toggle_list = set(parsed)
        self.toggle_on(toggle_list)
        # then parse what to remove:
        parsed = []
        geo_list = re.findall(geo_regex, negative_text)
        for i in geo_list:
            parsed.extend(geo_groups[i])
            negative_text = negative_text.replace(i, '')
        parsed.extend(re.findall(element_regex, negative_text))
        toggle_list = set(parsed)
        self.toggle_off(toggle_list)

    def toggle_on(self, toggle_list):
        for i in toggle_list:
            button = self.cellWidget(pt_indexes[i][0],  # pt_indexes is global dict
                                     pt_indexes[i][1])
            if button.isEnabled():
                button.setChecked(True)
                button.setStyleSheet("""font: bold;""")

    def clear_all(self):
        self.blockSignals(True)
        self.toggle_off(geo_groups['ALL'])
        self.blockSignals(False)
        self.allElementsOff.emit()

    def toggle_off(self, toggle_list):
        for i in toggle_list:
            button = self.cellWidget(pt_indexes[i][0],
                                     pt_indexes[i][1])
            if button.isEnabled():
                button.setChecked(False)
                button.setStyleSheet("""font: normal;""")

    def _populate_table(self, elements=[]):
        self.signalMapper2 = QtCore.QSignalMapper(self)
        self.signalMapper2.mapped[Qt.QWidget].connect(self.elementToggler)
        for i in pt_indexes:
            pt_button = HoverableButton(i)
            pt_button.setStyleSheet("""
                                    padding-left: 5px;
                                    padding-right: 3px;
                                    padding-top: 1px;
                                    padding-bottom: 1px;""")
            if i in elements:
                pt_button.setChecked(True)
            self.setCellWidget(pt_indexes[i][0],
                               pt_indexes[i][1],
                               pt_button)
            pt_button.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            pt_button.toggled.connect(self.signalMapper2.map)
            self.signalMapper2.setMapping(pt_button, pt_button)
        line = Qt.QFrame()
        line.setFrameShape(Qt.QFrame.HLine)
        line.setFrameShadow(Qt.QFrame.Sunken)
        self.setCellWidget(6, 3, line)
        #dissable inert gasses, H and Li:
        for i in ['H', 'He', 'Ne', 'Ar', 'Xe', 'Kr', 'Rn', 'Li']:
            self.cellWidget(pt_indexes[i][0],
                            pt_indexes[i][1]).setEnabled(False)
        lant_text = Qt.QLabel('Lan')
        act_text = Qt.QLabel('Act')
        lant_text.setAlignment(QtCore.Qt.AlignCenter)
        act_text.setAlignment(QtCore.Qt.AlignCenter)
        self.setCellWidget(5, 2, lant_text)
        self.setCellWidget(6, 2, act_text)
        lant_text.setEnabled(False)
        act_text.setEnabled(False)
        self.setMinimumWidth(self.horizontalHeader().length() + 10)

    def keyPressEvent(self, event):
        #if (event.key() >= 0x41) and (event.key() <= 0x5a):
        if event.key() == QtCore.Qt.Key_Shift:
            self.textInterface.setFocus()
        #that should be done from parent widget level:
        #elif(event.key() == Qt.Key_Escape):
        #    self.close()

    #@QtCore.pyqtSlot(Qt.QWidget)  #slot does not work due to lame pyqt5.7 regression
    def elementToggler(self, button):
        if button.isChecked():
            self.enableElement.emit(button.text())
            if button.hoverState:
                button.setGeometry(button.orig_size)
                button.setStyleSheet("""font: bold;""")
        else:
            self.disableElement.emit(button.text())
            button.setStyleSheet("""font: normal;""")
