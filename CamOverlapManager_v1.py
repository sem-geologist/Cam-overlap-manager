version= '0.8.0'
# Copyright Petras Jokubauskas 2016
    
import struct
from io import BytesIO
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
from glob import glob
import pickle

from datetime import datetime, timedelta
import os, sys

#GUIelements:
from GUI.mainwindow import Ui_MainWindow
from GUI import element_table_Qt5 as et

program_path = os.path.dirname(__file__)
try:
    import winreg
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"SOFTWARE\Cameca\SX\Configuration") as thingy:
        data_path = winreg.QueryValueEx(thingy, "DataPath")[0]
    qtiSet_path = os.path.join(data_path, 'Analysis Setups', 'Quanti')
except:
    logging.warning('Cameca PeakSight sotware were not dected on the system')

#for development and debugging on linux/bsd:
if os.name == 'posix':
    #the path with sample qtiSet files
    qtiSet_path = 'Quanti'

with open(os.path.join(program_path, 'about.html'), 'r') as about_html:
    about_text = about_html.read()

#handy functions
def filetime_to_datetime(filetime):
    """Return recalculated lame windows filetime to usable python (unix) datetime."""
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

    #instead of bellow dicts lists could be used, however,
    #python dict is much faster to lookup than list
    #and it is going to be looked up many many times
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
                    3: 'Lγ4', 4:'Lγ3', 5: 'Lγ2', 6: 'Lγ',
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
            filetime, change_len = struct.unpack('<Qi',fbio.read(12))
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
                logging.warning(html_colorify(self.file_basename + ".qtiSet got changed. refreshing...", 'yellow'))
                self.parse_thing(self.filename)
        else:
            logging.warning(html_colorify(self.file_basename + ".qtiSet got removed. The ovl file is orphaned.", 'yellow'))
            
    def parse_thing(self, filename):
        self.filename = filename
        with open(filename, 'br') as fn:
            #file bytes 
            fbio = BytesIO()
            fbio.write(fn.read())
        self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
        self.file_modification_date = mod_date(filename)
        self._read_the_header(fbio)
        if self.cameca_bin_file_type != 4:
            raise IOError(' '.join(['The file header shows it is not qtiSet',
                                    'file, but', self.file_type]))
        #parse data:
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
                #field_names2 = ['atom', 'line', 'spect no', 'xtal','2d','K']
                #field_values2 = struct.unpack('<3i4s2f', fbio.read(24))
                #fingerprint = fbio.read(16) # get binary fingerprint
                self.fingerprints.append(fbio.read(16))
                #thingy = (dict(zip(field_names2, field_values2)))
                fbio.seek(8, 1)
                str_len = struct.unpack('<i', fbio.read(4))[0]
                fbio.seek(420 + str_len, 1)  # skip irrelevant shit
                if self.file_version == 4:
                    fbio.seek(4, 1)


class CamecaOverlap(CamecaBase):
    def __init__(self, filename):
        self.filename = filename
        if os.path.exists(filename):
            logging.info(filename + 'exists. Opening...')
            with open(filename, 'br') as fn:
                #file bytes 
                self.fbio = BytesIO()
                self.fbio.write(fn.read())
            self.file_basename = os.path.basename(filename).rsplit('.', 1)[0]
            self.file_modification_date = mod_date(filename)
            self._read_the_header(self.fbio)
            if self.cameca_bin_file_type != 10:
                raise IOError(' '.join(['The file header shows it is not overlap',
                                       'file, but',
                                       self.file_type]))
            data_type, self.n_overlaps = struct.unpack('<2i', self.fbio.read(8))
            if data_type != 0:
                raise RuntimeError(''.join(['unexpected value of overlap struct: ',
                                            'instead of expected 0, the value ',
                                            str(data_type), ' at the address ',
                                            str(self.fbio.tell())]))
            self.overlaps = []
            for i in range(self.n_overlaps):
                self.overlaps.append(OverlapItem(self.fbio))
        else:
            logging.info(filename + 'does not exists. Creating new Overlap set...')
            self.file_comment = ''
            self.n_overlaps = 0
            self.overlaps = []
        
    def insert_overlap(self, index, overlap):
        self.overlaps.insert(index, overlap)
        self.n_overlaps += 1
        
    def remove_overlap(self, index):
        del self.overlaps[index]
        self.n_overlaps -= 1
            
    def _initiate_with_header(self, version=3, changes=''):
        """
        create and return BytesIO stream initiated with given header information
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
    
    def save_to_file(self,version=3):
        self.fbio = self._initiate_with_header(version=version)
        self.fbio.write(struct.pack('<2i', 0, self.n_overlaps))
        for i in self.overlaps:
            self.fbio.write(i.raw_str)
        self.fbio.seek(0)
        with open(self.filename, 'bw') as fn:
            #file bytes 
            fn.write(self.fbio.read())

class OverlapItem(object):
    def __init__(self, fbio):
        #we save raw string because we have few unknown values
        #this makes the saving of overlap information less demanding:
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
        self.fingerprint = struct.pack('<3i4s',self.atom, self.line, self.spect_nr, self.spect_name)
        
        
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


class TreeItem(CamecaBase):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children (file-record relationship)
    '''    
    def __init__(self, node, parent=None):
        self.node = node
        self._children = []
        self._parent = parent
        
        if parent is not None:
            parent.addChild(self)
    
    def no_child_condition(self):
        return position < 0 or position > len(self._children) or\
          type(self.node) != CamecaOverlap
    
    def setParent(self, parent):
        self._parent = parent
        parent.addChild(self)
    
    def addChild(self, child):
        self._children.append(child)

    def insertChild(self, position, child):
        if no_child_condition:
            return False  
        self._children.insert(position, child)
        child._parent = self
        return True

    def removeChild(self, position):
        if no_child_condition:
            return False
        child = self._children.pop(position)
        child._parent = None
        return True

    def child(self, row):
        return self._children[row]
    
    def childCount(self):
        return len(self._children)

    def parent(self):
        return self._parent
    
    def row(self):
        if self._parent is not None:
            return self._parent._children.index(self)

    def columnCount(self):
        return 13
    
    def data(self, column):
        if type(self.node) == CamecaOverlap:
            if column == 0:
                return self.node.file_basename
            if column == 1:
                return QtCore.QDateTime(self.node.file_modification_date)                
        elif type(self.node) == OverlapItem:
            if column == 2:
                return ' '.join([self.to_element(self.node.atom),
                                 self.to_line(self.node.line)])
            elif column == 3:
                return ' '.join([self.to_element(self.node.i_atom),
                                 self.to_line(self.node.i_line)])
            elif column == 4:
                return self.node.order
            elif column == 5:
                return self.node.offset
            elif column == 6:
                return self.node.HV
            elif column == 7:
                return self.node.beam_cur
            elif column == 8:
                return self.node.peak_bkd
            elif column == 9:
                return self.node.std_name
            elif column == 10:
                return self.node.spect_nr
            elif column == 11:
                return self.node.spect_name.decode()[::-1] # rev str
            elif column == 12 and self.node.struct_type == 3:
                return self.node.dwelltime


class TreeOverlapModel(QtCore.QAbstractItemModel):
    
    HORIZONTAL_HEADERS = ["Name",  # 0
                      "date",
                      "elem.l.", # 2
                      "ovl.elem.l.",
                      "order",  # 4
                      "offset",
                      "HV",  # 6
                      "bm.cur.",
                      "pk-bkgd",  # 8
                      "standard",
                      "spec.",  # 10
                      "xtal",
                      "time [s]"]
    horizontal_header_tooltips = [
        "overlap corection file basename",
        "last modification date(time) of the file",
        "analysed element and x-ray line",
        "overlaping element and its x-ray line",
        "order of overlaping element",
        "relative position of overlaping element peak",
        "acceleration voltage",
        "beam current",
        "peak - background",
        "standard",
        "spectrometer number",
        "crystal type",
        "dwell time (seconds)"]
    
    def __init__(self, root, parent=None):
        super(TreeOverlapModel, self).__init__(parent)
        self._rootNode = root

    def rowCount(self, parent):
        if not parent.isValid():
            parentNode = self._rootNode
        else:
            parentNode = parent.internalPointer()
        return parentNode.childCount()

    def columnCount(self, parent):
        return 13
    
    def flags(self, index):
        if index.isValid():
            node = index.internalPointer()
            if type(node.node) == OverlapItem:
                return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |\
                    QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled
            elif type(node.node) == CamecaOverlap:
                return QtCore.Qt.ItemIsEnabled
        
        #else:
        #    return QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable |\
        #        QtCore.Qt.ItemIsDropEnabled
    
    def data(self, index, role):   
        if not index.isValid():
            return None

        node = index.internalPointer()

        if role == QtCore.Qt.DisplayRole:
            if index.column() == 1 and type(node.node) == CamecaOverlap:
                return node.data(index.column()).date()
            return node.data(index.column())
        if role == QtCore.Qt.ToolTipRole and index.column() < 2:
            return node.data(index.column())
        
        if role == QtCore.Qt.BackgroundRole and node.data(11) and index.column() >= 2:
            return cameca_colors[get_xtal(node.data(11))]
        
        if role == QtCore.Qt.ForegroundRole and node.data(11) and index.column() >= 2:
            return QtGui.QColor(0,0,0)

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            return self.HORIZONTAL_HEADERS[section]
        elif role == QtCore.Qt.ToolTipRole:
            return self.horizontal_header_tooltips[section]
    
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction

    def parent(self, index):
        node = self.getNode(index)
        parentNode = node.parent()
        if parentNode == self._rootNode:
            return QtCore.QModelIndex()
        return self.createIndex(parentNode.row(), 0, parentNode)
        
    def index(self, row, column, parent):
        parentNode = self.getNode(parent)
        childItem = parentNode.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def getNode(self, index):
        if index.isValid():
            node = index.internalPointer()
            if node:
                return node    
        return self._rootNode


class OverlapFileModel(QtCore.QAbstractTableModel, CamecaBase):
    """Model of Overlap file to be used with TableView.
    Contains methods for appending, removing and saving the data"""
    HORIZONTAL_HEADERS = ["elem.l.", # 2
                      "ovl.elem.l.",
                      "order",  # 4
                      "offset",
                      "HV",  # 6
                      "bm.cur.",
                      "pk-bkgd",  # 8
                      "standard",
                      "spec.",  # 10
                      "xtal",
                      "time [s]"]
    horizontal_header_tooltips = ["analysed element and x-ray line",
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
        return 11
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        if self.cam_overlaps is not None:
            return len(self.cam_overlaps.overlaps)
        else:
            return 0
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.HORIZONTAL_HEADERS[section]
            else:
                return str(section + 1)
        elif (role == QtCore.Qt.ToolTipRole) and\
          (orientation == QtCore.Qt.Horizontal):
            return self.horizontal_header_tooltips[section]
    
    def set_cameca_overlap(self, overlaps):
        self.beginResetModel()
        self.cam_overlaps = overlaps
        self.endResetModel()
        #at loading the new overlap file reset modified flag:
        self.modified = False
    
    def data(self, index, role):   
        if not index.isValid():
            return None

        column = index.column()
        node = self.cam_overlaps.overlaps[index.row()]

        if role == QtCore.Qt.DisplayRole:
            if column == 0:
                return ' '.join([self.to_element(node.atom),
                                 self.to_line(node.line)])
            elif column == 1:
                return ' '.join([self.to_element(node.i_atom),
                                 self.to_line(node.i_line)])
            elif column == 2:
                return node.order
            elif column == 3:
                return node.offset
            elif column == 4:
                return node.HV
            elif column == 5:
                return node.beam_cur
            elif column == 6:
                return node.peak_bkd
            elif column == 7:
                return node.std_name
            elif column == 8:
                return node.spect_nr
            elif column == 9:
                return node.spect_name.decode()[::-1] # reversing the string
            elif column == 10 and node.struct_type == 3:
                return node.dwelltime
            
        if role == QtCore.Qt.BackgroundRole:
            return cameca_colors[get_xtal(node.spect_name.decode()[::-1])]
        
        if role == QtCore.Qt.ForegroundRole:
            return QtGui.QColor(0,0,0)
        
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
        
        self.beginInsertRows(self.parent, position, position + len(rows)- 1)
        
        for i in range(len(rows)):
            self.cam_overlaps.insert_overlap(position, rows[i])
            logging.info(' '.join(['added', rows[i].__repr__()]))
            
        self.endInsertRows()
        self.modified = True
        return True
        
    def supportedDropActions(self):
        return QtCore.Qt.CopyAction
        
    def mimeTypes(self):
        return ["application/x-overlap_list"]
        
    def dropMimeData(self, mimedata, action, row, column, parentIndex):
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


class LeafFilterProxyModel(QtCore.QSortFilterProxyModel):
    """Proxy model which filters parent and children in the trees
    depending from parent/children filter results"""

    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''
        # Check if the current row matches
        if self.filter_accepts_row_itself(row_num, source_parent):
            return True
 
        # Traverse up all the way to root and check if any of them match
        if self.filter_accepts_any_parent(source_parent):
            return True
 
        # Finally, check if any of the children match and parent in datetime
        return self.has_accepted_children(row_num, source_parent)
 
    def filter_accepts_row_itself(self, row_num, parent):
        return super(LeafFilterProxyModel, self).filterAcceptsRow(row_num,
                                                                  parent)
        #return self.filterAcceptsRowAlt(row_num, parent)
 
    def filter_accepts_any_parent(self, parent):
        ''' Traverse to the root node and check if any of the
            ancestors match the filter
        '''
        while parent.isValid():
            if self.filter_accepts_row_itself(parent.row(), parent.parent()):
                return True
            parent = parent.parent()
        return False
 
    def has_accepted_children(self, row_num, parent):
        ''' Starting from the current node as root, traverse all
            the descendants and test if any of the children match
        '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, parent)
        date_ind = model.index(row_num, 1, parent)
        children_count =  model.rowCount(source_index)
        for i in range(children_count):
            if self.filterAcceptsRow(i, source_index):
                return True
        return False


class CascadingFilterModel(LeafFilterProxyModel):
    def __init__(self):
        super().__init__()
        self.original_model = None
        self.sort_elem_model = LeafFilterProxyModel()
        self.sort_interf_model = LeafFilterProxyModel()
        self.sort_interf_model.setSourceModel(self.sort_elem_model)
        self.setSourceModel(self.sort_interf_model)
        self.setFilterKeyColumn(0)
        self.sort_elem_model.setFilterKeyColumn(2)
        self.sort_interf_model.setFilterKeyColumn(3)
    
    def set_original_model(self, model):
        self.original_model = model
        self.sort_elem_model.setSourceModel(self.original_model)
    
    def setFilenameFilter(self, regexp):
        self.setFilterRegExp(regexp)
        
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
        return self.original_model.getNode(level2).node
    

class AvailableOverlapTreeView(QtWidgets.QTreeView):
    """custom treeview with drag (but not drop) enabled
       with custom MIME data produced for drag"""
    def __init__(self, parent=None):
        super().__init__()
        self.setMinimumSize(QtCore.QSize(300, 0))
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.header().setDefaultSectionSize(50)
        self.setObjectName("sourceTV")
    
    def startDrag(self, event):
        s_model = self.selectionModel()
        selected_rows = s_model.selectedRows()
        if selected_rows == []:
            return
        
        mimeData = QtCore.QMimeData()
        item_list = []
        for i in selected_rows:
            item_list.append(self.model().get_original_node(i))

        ## convert to  a bytestream
        bstream = pickle.dumps(item_list)
        mimeData.setData("application/x-overlap_list", bstream)
        
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        
        pixmap = QtGui.QPixmap()
        pixmap.load(os.path.join(program_path, 'icons/overlap.png'))

        drag.setPixmap(pixmap)
        drag.exec()
    
    def setColumnWidths(self):
        widths = [120,100,55,60,35,35,40,45,70,70,45,45]
        for i in range(len(widths)):
            self.setColumnWidth(i, widths[i])
        

class NewOverlapFileView(QtWidgets.QTreeView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setEnabled(True)
        self.setMinimumSize(QtCore.QSize(100, 0))
        self.setAcceptDrops(True)
        self.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DropOnly)
        self.setDefaultDropAction(QtCore.Qt.CopyAction)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        #self.setShowGrid(False)
        #self.setGridStyle(QtCore.Qt.NoPen)
        self.setSortingEnabled(False)
        self.setObjectName("overlap_file_view")
        #self.horizontalHeader().setDefaultSectionSize(60)
        #self.horizontalHeader().setSortIndicatorShown(False)
        #self.verticalHeader().setDefaultSectionSize(24)
        #self.verticalHeader().setSortIndicatorShown(False)
        
        
    def dragEnterEvent(self, event):
        print(event.mimeData().hasFormat("application/x-overlap_list"))
        if event.mimeData().hasFormat("application/x-overlap_list"):
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        print('trying to drop')
        mime_raw_data = event.mimeData().data("application/x-overlap_list")
        item_list = pickle.load(mime_raw_data)
        self.model().insertRows(0, item_list)
        


class QPlainTextEditLogger(logging.Handler):
    """class for customised logging Handler
    inteded to output the logs to
    provided QPlainTextEdit widget instance"""
    def __init__(self, widget):
        super().__init__()
        self.widget = widget #QtWidgets.QPlainTextEdit()
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendHtml(msg)

class MainWindow(Ui_MainWindow, QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.file_watcher = QtCore.QFileSystemWatcher()
        #create and add treeview for all overlaps:
        self.sourceTV = AvailableOverlapTreeView(self.availableOverlapsLayout)
        self.availableOverlapsLayout.addWidget(self.sourceTV, 1, 0, 1, 4)
        self.overlap_file_view = NewOverlapFileView(self.frame2)
        self.gridLayout_2.addWidget(self.overlap_file_view, 1, 1, 4, 1)
        #create and asign filter model to the tree view made before:
        self.filterModel = CascadingFilterModel()
        self.overlap_file_model = OverlapFileModel()
        self.overlap_file_view.setModel(self.overlap_file_model)
        self.sourceTV.setModel(self.filterModel)
        #connect text line edit interface with filtering model:
        self.lineEdit.textChanged.connect(self.changeNameFilter)
        self.el_line_protect = False
        #create overlap model and set it to be source model of filter model:
        self.create_available_overlaps_model(qtiSet_path)
        #adjust column width to content:
        self.sourceTV.expandAll()
        for i in range(12):
            self.sourceTV.resizeColumnToContents(i)
        #setup interface for element selection:
        self.element_selection = []
        self.elem_table = et.ElementTableGUI()
        self.elem_table.enableElement.connect(self.append_element)
        self.elem_table.disableElement.connect(self.remove_element)
        self.elem_table.allElementsOff.connect(self.reset_element)
        self.pet_button.clicked.connect(self.toggle_pet)
        #activating actions:
        self.actionAbout_Qt.triggered.connect(self.show_about_qt)
        self.actionAbout.triggered.connect(self.show_about)
        self.actionOpen_new_setup.triggered.connect(self.open_or_new_file)
        self.actionRemove.triggered.connect(self.delete_selected_entries)
        self.delete_button.pressed.connect(self.actionRemove.trigger)
        self.actionAppend_to_down.triggered.connect(self.append_selection_to_overlaps)
        self.append_to_ofv_button.pressed.connect(self.actionAppend_to_down.trigger)
        self.actionSave_setup.triggered.connect(self.save_to_file)
        self.actionExit.triggered.connect(self.close)
        self._setup_logging()
        self.sourceTV.setColumnWidths()
        self.file_watcher.addPath(qtiSet_path)
        self.file_watcher.directoryChanged.connect(self.refresh_data)
        self.file_watcher.fileChanged.connect(self.refresh_data)
        
    def _setup_logging(self):
        self.logTextBox = QPlainTextEditLogger(self.text_interface)
        self.logTextBox.setFormatter(logging.Formatter('%(asctime)s, %(levelname)s: %(message)s'))
        #global:
        logging.getLogger().addHandler(self.logTextBox)
        logging.getLogger().setLevel(logging.WARNING)
    
    def refresh_data(self):
        #reset qtiSet if available:
        if self.el_line_protect:
            self.qti_setup.refresh()
            self.check_coverage()
        self.create_available_overlaps_model(qtiSet_path)
    
    def changeNameFilter(self):
        self.filterModel.setFilenameFilter(self.lineEdit.text())
        self.sourceTV.expandAll()
        
    def changeElementFilter(self):
        if self.el_line_protect:
            self.filterModel.setOverlapingElementFilter(self.element_selection)
        else:
            self.filterModel.setElementFilter(self.element_selection)
        self.sourceTV.expandAll()
        
    def append_element(self, element):
        self.element_selection.append(element)
        self.changeElementFilter()
        self.sourceTV.expandAll()
        
    def remove_element(self, element):
        self.element_selection.remove(element)
        self.changeElementFilter()
        self.sourceTV.expandAll()
	
    def reset_element(self):
        self.element_selection = []
        self.changeElementFilter()
        self.sourceTV.expandAll()
        
    def create_available_overlaps_model(self, qtiDat_path):
        # the invisible root:
        item0 = TreeItem(None)

        ovl_list = glob(os.path.join(qtiDat_path, 'Overlap','*.ovl'))
        for i in ovl_list:
            ovl = CamecaOverlap(i)
            item2 = TreeItem(ovl, None)
            for j in ovl.overlaps:
                if not self.el_line_protect:
                    TreeItem(j, item2)
                elif j.fingerprint in self.qti_setup.fingerprints:
                    TreeItem(j, item2)
            if item2.childCount() > 0:
                item2.setParent(item0)
        
        self.available_ovl_model = TreeOverlapModel(item0)
        self.filterModel.set_original_model(self.available_ovl_model)
        
    def toggle_pet(self):
        """show or hide periodic element table"""
        #self.pet.setWindowOpacity(0.9)
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
                return self.save_modified_overlap_dlg()
            else:
                return True
    
    def check_coverage(self):
        not_covered = self.overlap_file_model.checkOverlapCover(self.qti_setup.fingerprints)
        if len(not_covered) > 0:   
            if self.remove_excesive_overlap_dlg():
                self.remove_excesive_overlaps(not_covered)
    
    def save_modified_overlap_dlg(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setText("The Overlap file has been modified.")
        dlg.setInformativeText("Do you want to save your changes?")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Save |\
                               QtWidgets.QMessageBox.Discard |\
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
            #don't do anything, return False to stop the parent function:
            return False

    def remove_excesive_overlap_dlg(self):
        dlg = QtWidgets.QMessageBox()
        dlg.setText("The excesive overlap entry(-ies) was/were detected."
            "It can cause PeakSight to malfunction or crash.")
        dlg.setInformativeText("Do you want to remove it/them?")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Yes |\
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
                basename, selected_ext = os.path.basename(filename).rsplit('.', 1)             
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
                logging.warning(html_colorify("Either Cameca changed the dir hierarchy,",'red'))
                logging.warning(html_colorify("or either you are trying to do something not conventional...", 'red'))
                logging.warning(html_colorify("opening/creating file in selected not-cannonical directory", 'yellow'))
                ovl_filename = filename + '.ovl'
                self.ovl_filename_label.setText(ovl_filename)
                self.el_line_protect = False
            self.overlap_file_model.set_cameca_overlap(CamecaOverlap(ovl_filename))
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
        dlg.setInformativeText("""before the appendment of selection to overlap model, the overlap file have to be opened or created in the next dialog""")
        dlg.setStandardButtons(QtWidgets.QMessageBox.Ok |\
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
    window.setWindowIcon(QtGui.QIcon(os.path.join(program_path, 'icons', 'overlap.png')))
    window.show()
    app.exec_()
