# Copyright Petras Jokubauskas 2016

import struct
from io import BytesIO
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
from glob import glob
import pickle
from operator import itemgetter

from datetime import datetime, timedelta
import os
import sys

# GUIelements:
from GUI.mainwindow2 import Ui_MainWindow
from GUI import element_table_Qt5 as et

version = '0.8.0'

program_path = os.path.dirname(__file__)
if os.name == 'nt':
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"SOFTWARE\Cameca\SX\Configuration") as thingy:
            data_path = winreg.QueryValueEx(thingy, "DataPath")[0]
        qtiSet_path = os.path.join(data_path, 'Analysis Setups', 'Quanti')
    except EnvironmentError:
        logging.warning(
            'Cameca PeakSight sotware were not dected on the system')

# for development and debugging on linux/bsd:
elif os.name == 'posix':
    # the path with sample qtiSet files
    qtiSet_path = 'Quanti'

with open(os.path.join(program_path, 'about.html'), 'r') as about_html:
    about_text = about_html.read()


# handy functions:
def filetime_to_datetime(filetime):
    """Return recalculated lame windows filetime
    to usable python (unix) datetime."""
    return datetime(1601, 1, 1) + timedelta(microseconds=filetime / 10)


def mod_date(filename):
    """Return datetime of file's last modification"""
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t)


def html_colorify(string, color):
    return r'<font color="{1}">{0}<\font>'.format(string, color)


cameca_colors = {'PC0': QtGui.QColor(182, 255, 182),
                 'PC1': QtGui.QColor(255, 255, 192),
                 'PC2': QtGui.QColor(255, 224, 192),
                 'PC3': QtGui.QColor(255, 192, 192),
                 'PET': QtGui.QColor(192, 192, 255),
                 'TAP': QtGui.QColor(175, 255, 255),
                 'LIF': QtGui.QColor(255, 192, 255)}


def get_xtal(full_xtal_name):
    """get basic crystal name.
       example: get_xtal('LLIF') -> 'LIF'
    """
    for i in ['PC0', 'PC1', 'PC2', 'PC3', 'PET', 'TAP', 'LIF']:
        if i in full_xtal_name:
            return i


class CamecaBase(object):
    """base class with cameca data type translating methods
    and cameca file header reader method useful
    for any other derived Reader/Writer class"""

    value_map = {
                 1: 'WDS setup',
                 2: 'Image/maping setup',
                 3: 'Calibration setup',
                 4: 'Quanti setup',
                 5: 'unknown',  # What is this???
                 6: 'WDS results',
                 7: 'Image/maping results',
                 8: 'Calibration results',
                 9: 'Quanti results',
                 10: 'Peak overlap table'
                }
    cameca_lines = {
                    1: 'Kβ', 2: 'Kα',
                    3: 'Lγ4', 4: 'Lγ3', 5: 'Lγ2', 6: 'Lγ',
                    7: 'Lβ9', 8: 'Lβ10', 9: 'Lβ7', 10: 'Lβ2',
                    11: 'Lβ6', 12: 'Lβ3', 13: 'Lβ4', 14: 'Lβ',
                    15: 'Lα', 16: 'Lν', 17: 'Ll',
                    18: 'Mγ', 19: 'Mβ', 20: 'Mα', 21: 'Mζ', 22: 'Mζ2',
                    23: 'M1N2', 24: 'M1N3', 25: 'M2N1', 26: 'M2N4',
                    27: 'M2O4', 28: 'M3N1', 29: 'M3N4', 30: 'M3O1',
                    31: 'M3O4', 32: 'M4O2'
                   }

    element_table = {
                     0: 'n', 1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B',
                     6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne', 11: 'Na',
                     12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S',
                     17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca', 21: 'Sc',
                     22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe',
                     27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn', 31: 'Ga',
                     32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr',
                     37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr', 41: 'Nb',
                     42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd',
                     47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn', 51: 'Sb',
                     52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba',
                     57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd', 61: 'Pm',
                     62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy',
                     67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb', 71: 'Lu',
                     72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os',
                     77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg', 81: 'Tl',
                     82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn',
                     87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th', 91: 'Pa',
                     92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm',
                     97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm', 101: 'Md',
                     102: 'No', 103: 'Lr'
                    }

    @classmethod
    def to_type(cls, sx_type):
        """return the string representation of cameca file type
        from given integer code"""
        return cls.value_map[sx_type]

    @classmethod
    def to_element(cls, number):
        """return atom name for given atom number"""
        return cls.element_table[number]

    @classmethod
    def to_line(cls, number):
        """ return stringof x-ray line from given cameca int code"""
        return cls.cameca_lines[number]

    def _read_the_header(self, fbio):
        """parse the header data into base cameca object atributes
        arguments:
        fbio -- file BytesIO object or the opened file
        """
        fbio.seek(0)
        a, b, c, d = struct.unpack('<B3sii', fbio.read(12))
        if b != b'fxs':
            raise IOError('The file is not a cameca peaksight software file')
        self.cameca_bin_file_type = a
        self.file_type = self.to_type(a)
        self.file_version = c
        self.file_comment = fbio.read(d).decode()
        fbio.seek(0x1C, 1)  # some spacer with unknown values
        n_changes = struct.unpack('<i', fbio.read(4))[0]
        self.changes = []
        for i in range(n_changes):
            filetime, change_len = struct.unpack('<Qi', fbio.read(12))
            comment = fbio.read(change_len).decode()
            self.changes.append([filetime_to_datetime(filetime),
                                 comment])
        if self.file_version == 4:
            fbio.seek(0x08, 1)


class CamecaQtiSetup(CamecaBase):
    def __init__(self, filename):
        self.parse_thing(filename)

    def refresh(self):
        if os.path.isfile(self.filename):
            if mod_date(self.filename) != self.file_modification_date:
                warnung = ".".join([self.file_basename,
                                    "qtiSet got changed. refreshing..."])
                logging.warning(html_colorify(warnung, 'yellow'))
                self.parse_thing(self.filename)
        else:
            warnung = ".".join([self.file_basename,
                                "qtiSet got removed",
                                " The ovl file is orphaned."])
            logging.warning(html_colorify(warnung, 'yellow'))

    def parse_thing(self, filename):
        self.filename = filename
        with open(filename, 'br') as fn:
            # file bytes
            fbio = BytesIO()
            fbio.write(fn.read())
        self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
        self.file_modification_date = mod_date(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != 4:
            raise IOError(' '.join(['The file header shows it is not qtiSet',
                                    'file, but', self.file_type]))
        # parse data:
        fbio.seek(12, 1)  # unknown shit
        self.n_options = struct.unpack('<i', fbio.read(4))[0]
        self.fingerprints = []
        self.options = {}
        for i in range(self.n_options):
            fbio.seek(32, 1)  # skip another junk
            field_names = ['heat', 'HV', 'unkn1',
                           'Xhi', 'Yhi', 'Xlo',
                           'Ylo', 'apert_X', 'apert_Y', 'C1',
                           'C2', 'unkn2', 'current',
                           'BFocus', 'unkn3', 'unkn4', 'BFocus2',
                           'size', 'asti_amp', 'asti_deg']
            field_values = struct.unpack('<20i', fbio.read(80))
            self.options[i] = dict(zip(field_names, field_values))
            fbio.seek(424, 1)  # skip not so relevant information and junk
            elements = struct.unpack('<i', fbio.read(4))[0]
            for j in range(elements):
                # field_names2 = ['atom', 'line', 'spect no', 'xtal','2d','K']
                # field_values2 = struct.unpack('<3i4s2f', fbio.read(24))
                # fingerprint = fbio.read(16) # get binary fingerprint
                self.fingerprints.append(fbio.read(16))
                # thingy = (dict(zip(field_names2, field_values2)))
                fbio.seek(8, 1)
                str_len = struct.unpack('<i', fbio.read(4))[0]
                fbio.seek(420 + str_len, 1)  # skip irrelevant shit
                if self.file_version == 4:
                    fbio.seek(4, 1)


class CamecaOverlap(CamecaBase):
    def __init__(self, filename=None):
        self.filename = filename
        if filename is None:
            self.n_overlaps = 0
            self.overlaps = []
        elif os.path.exists(filename):
            logging.info(filename + 'exists. Opening...')
            with open(filename, 'br') as fn:
                # file bytes:
                self.fbio = BytesIO()
                self.fbio.write(fn.read())
            self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
            self.file_modification_date = mod_date(filename)
            self._read_the_header(self.fbio)
            if self.cameca_bin_file_type != 10:
                raise IOError(' '.join(['The file header shows it is not',
                                        'overlap file, but',
                                        self.file_type]))
            data_type, self.n_overlaps = struct.unpack('<2i',
                                                       self.fbio.read(8))
            if data_type != 0:
                raise RuntimeError(' '.join(['unexpected value of overlap',
                                             'struct: instead of expected',
                                             '0, the value',
                                             str(data_type),
                                             'at the address',
                                             str(self.fbio.tell())]))
            self.overlaps = []
            for i in range(self.n_overlaps):
                item = OverlapItem(self.fbio)
                item.append_metadata([self.file_modification_date,
                                      self.file_basename])
                self.overlaps.append(item)
        else:
            logging.info(filename +
                         'does not exists. Creating new Overlap set...')
            self.file_comment = ''
            self.n_overlaps = 0
            self.overlaps = []

    def insert_overlap(self, index, overlap):
        self.overlaps.insert(index, overlap)
        self.n_overlaps += 1

    def remove_overlap(self, index):
        del self.overlaps[index]
        self.n_overlaps -= 1

    def append_unique_overlap(self, overlap):
        if overlap in self.overlaps:
            item = self.overlaps[self.overlaps.index(overlap)]
            item.append_metadata(overlap.metadata[0])
        else:
            self.overlaps.append(overlap)
            self.n_overlaps += 1

    def _initiate_with_header(self, version=3, changes=''):
        """
        create and return BytesIO stream initiated with given header
        information.
        fyle_type -- coded int value of cameca file/data type
        version -- version of the file (default 3)
        comment -- string with comment of file (default empty string)
        changes -- default is empty string (is not going to be implimented)
        """
        fbio = BytesIO()
        comment = self.file_comment
        fbio.write(struct.pack('<B3sii', 10, b'fxs',
                               version, len(comment.encode())))
        pack_str = ''.join(['<', str(len(comment.encode())), 's'])
        fbio.write(struct.pack(pack_str, comment.encode()))
        fbio.write(0x1C * b'\x00')
        pack_str = ''.join(['<i', str(len(changes.encode())), 's'])
        fbio.write(struct.pack(pack_str, len(changes), changes.encode()))
        if version == 4:
            fbio.write(0x08 * b'\x00')
        return fbio

    def save_to_file(self, version=3):
        self.fbio = self._initiate_with_header(version=version)
        self.fbio.write(struct.pack('<2i', 0, self.n_overlaps))
        for i in self.overlaps:
            self.fbio.write(i.raw_str)
        self.fbio.seek(0)
        with open(self.filename, 'bw') as fn:
            # file bytes
            fn.write(self.fbio.read())


class OverlapItem(object):
    def __init__(self, fbio):
        # we save raw string because we have few unknown values
        # this makes the saving of overlap information less demanding:
        if type(fbio) == BytesIO:
            self.raw_str = fbio.read(44)
            self._first_initiate()
            std_name = fbio.read(self.str_len)
            self.raw_str += std_name
            spect = fbio.read(12)
            self.raw_str += spect
            self.unknown1, self.spect_nr, self.spect_name = struct.unpack(
                '<2i4s', spect)
            if self.struct_type == 3:  # only version 3
                the_rest = fbio.read(8)
                self.raw_str += the_rest
                self.dwelltime, self.unknown2 = struct.unpack('<fi', the_rest)
        elif type(fbio) == bytes:
            self.raw_str = fbio
            self._first_initiate()
            i = 44 + self.str_len
            std_name = fbio[44:i]
            self.unknown1, self.spect_nr, self.spect_name = struct.unpack(
                '<2i4s', fbio[i:i+12])
            if self.struct_type == 3:  # only version 3
                self.dwelltime, self.unknown2 = struct.unpack('<fi',
                                                              fbio[i+12:i+20])
        self.std_name = std_name.decode()
        self.fingerprint = struct.pack('<3i4s', self.atom, self.line,
                                       self.spect_nr, self.spect_name)
        self.metadata = []
        self.n_metadata = 0

    def _first_initiate(self):
        self.struct_type, self.atom, self.line, self.i_atom,\
            self.i_line, self.order, self.offset, self.HV, self.beam_cur,\
            self.peak_bkd, self.str_len = struct.unpack('<7i3fi',
                                                        self.raw_str[:44])

    def __repr__(self):
        return ' '.join([CamecaBase.to_element(self.i_atom),
                         CamecaBase.to_line(self.i_line),
                         'overlap with',
                         CamecaBase.to_element(self.atom),
                         CamecaBase.to_line(self.line)])

    def __eq__(self, other):
        return self.raw_str == other.raw_str

    def append_metadata(self, metadata=[]):
        self.metadata.append(metadata)
        self.n_metadata += 1
        self.metadata.sort(key=itemgetter(0))
        self.oldest = self.metadata[0][0]

    def oldest_newest(self):
        old_n_new = [self.metadata[0], self.metadata[-1]]
        a, b, c, d = [item for sublist in old_n_new for item in sublist]
        thingy = 'oldest: {0} {1}\nnewest: {2} {3}'.format(a, b, c, d)
        return thingy


class OverlapFileModel(QtCore.QAbstractTableModel, CamecaBase):
    """Model of Overlap file to be used with TableView.
    Contains methods for appending, removing and saving the data"""
    HORIZONTAL_HEADERS = ["oldest use",
                          "n.labels",
                          "elem.l.",
                          "ovl.e.l.",
                          "ord.",
                          "off.",
                          "HV",
                          "beam",
                          "pk-bg",
                          "std.",
                          "sp.",
                          "XTAL",
                          "time [s]"]
    horizontal_header_tooltips = ["oldest modification of overlap file",
                                  "number of labels which use the overlap",
                                  "analysed element and x-ray line",
                                  "overlaping element and its line",
                                  "order of overlaping element",
                                  "offset of overlaping element peak",
                                  "acceleration voltage",
                                  "beam current",
                                  "Peak - background",
                                  "standard",
                                  "spectrometer number",
                                  "crystal type",
                                  "dwell time (seconds)"]

    def __init__(self):
        super().__init__()
        self.cam_overlaps = None
        self.modified = False
        self.parent = QtCore.QModelIndex()

    def columnCount(self, parent=QtCore.QModelIndex()):
        return 13

    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.cam_overlaps is not None:
            return len(self.cam_overlaps.overlaps)
        else:
            return 0

    def headerData(self, section, orientation, role):
        if orientation == QtCore.Qt.Horizontal:
            if role == QtCore.Qt.DisplayRole:
                return self.HORIZONTAL_HEADERS[section]
            elif role == QtCore.Qt.ToolTipRole:
                return self.horizontal_header_tooltips[section]

    def set_cameca_overlap(self, overlaps):
        self.beginResetModel()
        self.cam_overlaps = overlaps
        self.endResetModel()
        # at loading the new overlap file reset modified flag:
        self.modified = False

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid():
            return None

        column = index.column()
        node = self.cam_overlaps.overlaps[index.row()]

        if role == QtCore.Qt.ToolTipRole and index.column() == 1:
            return node.oldest_newest()

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return QtCore.QDate(node.oldest)
            if column == 1:
                return node.n_metadata
            if column == 2:
                return ' '.join([self.to_element(node.atom),
                                 self.to_line(node.line)])
            elif column == 3:
                return ' '.join([self.to_element(node.i_atom),
                                 self.to_line(node.i_line)])
            elif column == 4:
                return node.order
            elif column == 5:
                return node.offset
            elif column == 6:
                return node.HV
            elif column == 7:
                return node.beam_cur
            elif column == 8:
                return node.peak_bkd
            elif column == 9:
                return node.std_name
            elif column == 10:
                return node.spect_nr
            elif column == 11:
                return node.spect_name.decode()[::-1]  # reversing the string
            elif column == 12 and node.struct_type == 3:
                return node.dwelltime

        if role == QtCore.Qt.BackgroundRole:
            return cameca_colors[get_xtal(node.spect_name.decode()[::-1])]

        if role == QtCore.Qt.ForegroundRole:
            return QtGui.QColor(0, 0, 0)

    def insertRows(self, position, rows=[]):
        for i in self.cam_overlaps.overlaps:
            for j in rows:
                if i.raw_str == j.raw_str:
                    logging.warning(html_colorify(
                        ' '.join(['identical', j.__repr__(),
                                  'already presented. Skipping....']),
                        'yellow'))
                    rows.remove(j)
        if rows == []:
            return False
        self.beginInsertRows(self.parent, position, position + len(rows) - 1)
        for i in range(len(rows)):
            self.cam_overlaps.insert_overlap(position, rows[i])
            logging.info(' '.join(['added', rows[i].__repr__()]))
        self.endInsertRows()
        self.modified = True
        return True

    def deleteRows(self, rows=[]):
        if rows == []:
            return False
        self.beginResetModel()
        rows.sort(reverse=True)
        for i in rows:
            self.cam_overlaps.remove_overlap(i)
        self.endResetModel()
        self.modified = True
        return True

    def checkOverlapCover(self, fingerprints):
        not_covered = []
        for i in range(len(self.cam_overlaps.overlaps)):
            if self.cam_overlaps.overlaps[i].fingerprint not in fingerprints:
                not_covered.append(i)
        return not_covered

    def getNode(self, index):
        if index.isValid():
            node = self.cam_overlaps.overlaps[index.row()]
            if node is not None:
                return node


class DateFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Proxy model which filters parent and children in the trees
    depending from parent/children filter results"""

    def setFilterMinimumDate(self, date):
        self._minDate = date
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        """Overriding the parent function to check
        check the date is not too old"""
        if self.filterKeyColumn() == 0:
            # Fetch datetime value.
            index = self.sourceModel().index(sourceRow, 0, sourceParent)
            return self.sourceModel().data(index) > self._minDate
        # Not our business.
        return super(DateFilterProxyModel, self).filterAcceptsRow(sourceRow,
                                                                  sourceParent)


class CascadingFilterModel(DateFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.original_model = None
        self.sort_elem_model = DateFilterProxyModel()
        self.sort_interf_model = DateFilterProxyModel()
        self.sort_interf_model.setSourceModel(self.sort_elem_model)
        self.setSourceModel(self.sort_interf_model)
        self.setFilterKeyColumn(0)
        self.setFilterMinimumDate(QtCore.QDate(2014, 1, 1))
        self.sort_elem_model.setFilterKeyColumn(2)
        self.sort_interf_model.setFilterKeyColumn(3)

    def set_original_model(self, model):
        self.original_model = model
        self.sort_elem_model.setSourceModel(self.original_model)

    def setElementFilter(self, element_list):
        regex = '\\s|'.join(element_list) + '\\s'
        self.sort_elem_model.setFilterRegExp(regex)
        self.sort_interf_model.setFilterRegExp(regex)

    def setMeasuredElementFilter(self, element_list):
        regex = '\\s|'.join(element_list) + '\\s'
        self.sort_elem_model.setFilterRegExp(regex)

    def setOverlapingElementFilter(self, element_list):
        regex = '\\s|'.join(element_list) + '\\s'
        self.sort_interf_model.setFilterRegExp(regex)

    def get_original_node(self, index):
        level0 = self.mapToSource(index)
        level1 = self.sort_interf_model.mapToSource(level0)
        level2 = self.sort_elem_model.mapToSource(level1)
        return self.original_model.getNode(level2)


class QPlainTextEditLogger(logging.Handler):
    """class for customised logging Handler
    inteded to output the logs to
    provided QPlainTextEdit widget instance"""
    def __init__(self, widget):
        super().__init__()
        self.widget = widget  # QtWidgets.QPlainTextEdit()
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendHtml(msg)


class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.file_watcher = QtCore.QFileSystemWatcher()
        # create and asign filter model to the tree view made before:
        self.filterModel = CascadingFilterModel()
        self.overlap_file_model = OverlapFileModel()
        self.overlap_file_view.setModel(self.overlap_file_model)
        self.sourceTV.setModel(self.filterModel)
        # connect text line edit interface with filtering model:
        self.minDateEdit.dateChanged.connect(
            self.filterModel.setFilterMinimumDate)
        self.el_line_protect = False
        # create overlap model and set it to be source model of filter model:
        self.create_available_overlaps_model(qtiSet_path)
        # setup interface for element selection:
        self.element_selection = []
        self.elem_table = et.ElementTableGUI()
        self.elem_table.enableElement.connect(self.append_element)
        self.elem_table.disableElement.connect(self.remove_element)
        self.elem_table.allElementsOff.connect(self.reset_element)
        self.pet_button.clicked.connect(self.toggle_pet)
        # activating actions:
        self.actionAbout_Qt.triggered.connect(self.show_about_qt)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionOpen_new_setup.triggered.connect(self.open_or_new_file)
        self.actionRemove.triggered.connect(self.delete_selected_entries)
        self.delete_button.pressed.connect(self.actionRemove.trigger)
        self.actionAppend_to_down.triggered.connect(
            self.append_selection_to_overlaps)
        self.append_to_ofv_button.pressed.connect(
            self.actionAppend_to_down.trigger)
        self.actionSave_setup.triggered.connect(self.save_to_file)
        self.actionExit.triggered.connect(self.close)
        self._setup_logging()
        widths = [100, 35, 60, 65, 35, 45, 40, 55, 75, 75, 40, 45, 60]
        for i in range(len(widths)):
            self.sourceTV.setColumnWidth(i, widths[i])
            self.overlap_file_view.setColumnWidth(i, widths[i]+5)
        ofv_header = self.overlap_file_view.horizontalHeader()
        ofv_header.setSectionsMovable(True)
        self.overlap_file_view.hideColumn(0)
        self.overlap_file_view.hideColumn(1)
        self.file_watcher.addPath(qtiSet_path)
        self.file_watcher.directoryChanged.connect(self.refresh_data)
        self.file_watcher.fileChanged.connect(self.refresh_data)

    def _setup_logging(self):
        self.logTextBox = QPlainTextEditLogger(self.text_interface)
        self.logTextBox.setFormatter(logging.Formatter(
            '%(asctime)s, %(levelname)s: %(message)s'))
        # global:
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.WARNING)

    def refresh_data(self):
        # reset qtiSet if available:
        if self.el_line_protect:
            self.qti_setup.refresh()
            self.check_coverage()
        self.create_available_overlaps_model(qtiSet_path)

    def changeElementFilter(self):
        if self.el_line_protect:
            self.filterModel.setOverlapingElementFilter(self.element_selection)
        else:
            self.filterModel.setElementFilter(self.element_selection)

    def append_element(self, element):
        self.element_selection.append(element)
        self.changeElementFilter()

    def remove_element(self, element):
        self.element_selection.remove(element)
        self.changeElementFilter()

    def reset_element(self):
        self.element_selection = []
        self.changeElementFilter()

    def create_available_overlaps_model(self, qtiDat_path):
        self.available_ovl_model = OverlapFileModel()
        overlap_agregate = CamecaOverlap()
        ovl_list = glob(os.path.join(qtiDat_path, 'Overlap', '*.ovl'))
        overleafs = [CamecaOverlap(k) for k in ovl_list]
        for i in overleafs:
            for j in i.overlaps:
                if not self.el_line_protect:
                    overlap_agregate.append_unique_overlap(j)
                elif j.fingerprint in self.qti_setup.fingerprints:
                    overlap_agregate.append_unique_overlap(j)
        self.available_ovl_model.set_cameca_overlap(overlap_agregate)
        self.filterModel.set_original_model(self.available_ovl_model)

    def toggle_pet(self):
        """show or hide periodic element table"""
        if self.elem_table.isVisible():
            self.elem_table.hide()
        else:
            self.elem_table.show()

    def show_about_qt(self):
        QtWidgets.QMessageBox.aboutQt(self)

    def show_about(self):
        QtWidgets.QMessageBox.about(self, 'About', about_text)

    def check_model_state(self):
        if self.overlap_file_model.cam_overlaps is None:
            return True
        else:
            if self.overlap_file_model.modified:
                self.check_coverage()
                return self.save_modified_overlap_dlg()
            else:
                return True

    def check_coverage(self):
        not_covered = self.overlap_file_model.checkOverlapCover(
            self.qti_setup.fingerprints)
        if len(not_covered) > 0:
            if self.remove_excesive_overlap_dlg():
                self.remove_excesive_overlaps(not_covered)

    def save_modified_overlap_dlg(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setText("The Overlap file has been modified.")
        dlg.setInformativeText("Do you want to save your changes?")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Save |
                               QtWidgets.QMessageBox.Discard |
                               QtWidgets.QMessageBox.Cancel)
        dlg.setDefaultButton(QtWidgets.QMessageBox.Save)
        dlg.setIcon(QtWidgets.QMessageBox.Question)
        ret = dlg.exec()
        if ret == QtWidgets.QMessageBox.Save:
            self.save_to_file()
            return True
        if ret == QtWidgets.QMessageBox.Discard:
            # to discard the model changes we do completely nothing:
            # and return True to go with procedure
            return True
        if ret == QtWidgets.QMessageBox.Cancel:
            # don't do anything, return False to stop the parent function:
            return False

    def remove_excesive_overlap_dlg(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setText("The excesive overlap entry(-ies) was/were detected."
                    "It can cause PeakSight to malfunction or crash.")
        dlg.setInformativeText("Do you want to remove it/them?")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Yes |
                               QtWidgets.QMessageBox.No)
        dlg.setDefaultButton(QtWidgets.QMessageBox.Yes)
        dlg.setIcon(QtWidgets.QMessageBox.Question)
        ret = dlg.exec()
        if ret == QtWidgets.QMessageBox.Yes:
            return True
        return False

    def remove_excesive_overlaps(self, not_covered):
        if self.overlap_file_model.deleteRows(not_covered):
            logging.info(str(len(not_covered)) + ' got removed')
        else:
            logging.warning('removing of selected entries failed')

    def save_to_file(self):
        if self.overlap_file_model.cam_overlaps is not None:
            self.file_watcher.blockSignals(True)
            if self.el_line_protect:
                v = self.qti_setup.file_version
            else:
                v = 3
            self.overlap_file_model.cam_overlaps.save_to_file(version=v)
            self.overlap_file_model.modified = False
            self.file_watcher.blockSignals(False)

    def delete_selected_entries(self):
        smodt = self.overlap_file_view.selectionModel()
        sel_rows = [i.row() for i in smodt.selectedRows()]
        if self.overlap_file_model.deleteRows(sel_rows):
            logging.info(str(len(sel_rows)) + ' got removed')
        else:
            logging.warning('removing of selected entries failed')

    def open_or_new_file(self):
        if not self.check_model_state():
            return
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        dlg.setDirectory(qtiSet_path)
        dlg.setNameFilter("peaksight Quanti or Overlap data (*.qtiSet *.ovl)")
        if dlg.exec_():
            filename = dlg.selectedFiles()[0]
            try:
                basename, selected_ext = os.path.basename(filename).rsplit('.',
                                                                           1)
            except ValueError:
                basename = os.path.basename(filename)
                selected_ext = ''
            dirname = os.path.dirname(filename)
            dirbasename = os.path.split(dirname)[-1]
            if (selected_ext == 'ovl') and (dirbasename == 'Overlap'):
                ovl_filename = filename
                self.ovl_filename_label.setText(
                                    os.path.join('Overlap', basename + '.ovl'))
                qti_setup_file = os.path.join('../', basename + '.qtiSet')
                if os.path.isfile(qti_setup_file):
                    self.el_line_protect = True
                else:
                    self.el_line_protect = False
            elif (selected_ext == 'qtiSet') and (dirbasename == 'Quanti'):
                qti_setup_file = filename
                ovl_filename = os.path.join(dirname,
                                            'Overlap',
                                            basename + '.ovl')
                self.ovl_filename_label.setText(
                                    os.path.join('Overlap', basename + '.ovl'))
                self.el_line_protect = True
            else:
                warnung = "Either Cameca changed the dir hierarchy,\n"\
                    "or either you are trying to do something not"\
                    "conventional..."
                warninfo = "opening/creating file in selected not-cannonical"\
                    "directory"
                logging.warning(html_colorify(warnung, 'red'))
                logging.warning(html_colorify(warninfo, 'yellow'))
                ovl_filename = filename + '.ovl'
                self.ovl_filename_label.setText(ovl_filename)
                self.el_line_protect = False
            self.overlap_file_model.set_cameca_overlap(
                CamecaOverlap(ovl_filename))
            if self.el_line_protect:
                self.qti_setup = CamecaQtiSetup(qti_setup_file)
                self.check_coverage()
                self.file_watcher.removePaths(self.file_watcher.files())
                self.file_watcher.addPath(qti_setup_file)
            self.create_available_overlaps_model(qtiSet_path)
            return True
        else:
            return False

    def model_not_initialized_dlg(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setText("The output overlap file is not initiated")
        dlg.setInformativeText("before the appendment of selection"
                               " to overlap model, the overlap file have"
                               " to be opened or created in the next dialog")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok |
                               QtWidgets.QMessageBox.Cancel)
        dlg.setDefaultButton(QtWidgets.QMessageBox.Ok)
        dlg.setIcon(QtWidgets.QMessageBox.Information)
        ret = dlg.exec()
        if ret == QtWidgets.QMessageBox.Ok:
            return self.open_or_new_file()
        if ret == QtWidgets.QMessageBox.Cancel:
            return False

    def append_selection_to_overlaps(self):
        """append selected overlaps from source tree view
        to the constructed overlap model"""
        if self.overlap_file_model.cam_overlaps is None:
            if not self.model_not_initialized_dlg():
                return
        smod = self.sourceTV.selectionModel()
        tvmodel = self.sourceTV.model()
        rows = [tvmodel.get_original_node(i) for i in smod.selectedRows()]

        self.overlap_file_model.insertRows(0, rows=rows)

    def closeEvent(self, event):
        state = self.check_model_state()

        if state:
            self.elem_table.close()  # be sure to close the element table too
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle(' '.join(['Cam-overlap-manager', version]))
    window.setWindowIcon(
        QtGui.QIcon(os.path.join(program_path, 'icons', 'overlap.png')))
    app.setStyle("Fusion")
    from PyQt5.QtGui import QPalette, QColor
    from PyQt5.QtCore import Qt
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)

    app.setPalette(dark_palette)

    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")
    
    window.show()
    app.exec_()
