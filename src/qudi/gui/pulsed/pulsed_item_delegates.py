# -*- coding: utf-8 -*-

"""
This file contains item delegates for the pulse editor QTableView/model.

.. Copyright (c) 2021, the qudi developers. See the AUTHORS.md file at the top-level directory of this
.. distribution and on <https://github.com/Ulm-IQO/qudi-iqo-modules/>
.. 
.. This file is part of qudi.
.. 
.. Qudi is free software: you can redistribute it and/or modify it under the terms of
.. the GNU Lesser General Public License as published by the Free Software Foundation,
.. either version 3 of the License, or (at your option) any later version.
.. 
.. Qudi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
.. without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
.. See the GNU Lesser General Public License for more details.
.. 
.. You should have received a copy of the GNU Lesser General Public License along with qudi.
.. If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from PySide2 import QtCore, QtGui, QtWidgets
from qudi.gui.pulsed.pulsed_custom_widgets import MultipleCheckboxWidget, AnalogParametersWidget
from qudi.util.widgets.scientific_spinbox import ScienDSpinBox


class CheckBoxItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, data_access_role=QtCore.Qt.DisplayRole):
        """
Parameters
----------
parent : QWidget
    The parent QWidget which hosts this child widget.
data_access_role : int, optional
    Role for data access, default is QtCore.Qt.DisplayRole.
"""

        super().__init__(parent)
        self._access_role = data_access_role
        return

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
QtWidgets.QCheckBox
    An editor widget that is a checkbox for user interaction.
"""

        editor = QtWidgets.QCheckBox(parent=parent)
        editor.setGeometry(option.rect)
        editor.stateChanged.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self):
        return QtCore.QSize(15, 50)

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role)
        if not isinstance(data, bool):
            return
        editor.blockSignals(True)
        editor.setChecked(data)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.isChecked()
        # write the data to the model:
        model.setData(index, data, self._access_role)
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        widget = QtWidgets.QCheckBox()
        widget.setGeometry(r)
        widget.setChecked(index.data(self._access_role))
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()


class SpinBoxItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, item_dict=None, data_access_role=QtCore.Qt.DisplayRole):
        """
Parameters
----------
parent : QWidget
    The parent QWidget which hosts this child widget.
item_dict : dict, optional
    Dictionary with configuration options for the editor.
data_access_role : int, optional
    Role for data access, default is QtCore.Qt.DisplayRole.
"""

        super().__init__(parent)
        if item_dict is None:
            item_dict = dict()
        self.item_dict = item_dict
        self._access_role = data_access_role
        return

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
QtWidgets.QSpinBox
    A spinbox editor for user interaction.
"""

        editor = QtWidgets.QSpinBox(parent=parent)
        if 'min' in self.item_dict:
            editor.setMinimum(self.item_dict['min'])
        if 'max' in self.item_dict:
            editor.setMaximum(self.item_dict['max'])
        if 'unit' in self.item_dict:
            editor.setSuffix(self.item_dict['unit'])
        editor.setGeometry(option.rect)
        editor.editingFinished.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self):
        return QtCore.QSize(90, 50)

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role)
        if not isinstance(data, (np.integer, int)):
            data = self.item_dict['init_val']
        editor.blockSignals(True)
        editor.setValue(int(data))
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.value()
        # write the data to the model:
        model.setData(index, data, self._access_role)
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        widget = QtWidgets.QSpinBox()
        if 'min' in self.item_dict:
            widget.setMinimum(self.item_dict['min'])
        if 'max' in self.item_dict:
            widget.setMaximum(self.item_dict['max'])
        if 'unit' in self.item_dict:
            widget.setSuffix(self.item_dict['unit'])
        widget.setGeometry(r)
        widget.setValue(index.data(self._access_role))
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()


class ScienDSpinBoxItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, item_dict, data_access_role=QtCore.Qt.DisplayRole):
        """
Parameters
----------
parent : QWidget
    The parent QWidget which hosts this child widget.
item_dict : dict
    Dictionary with configuration options for the spinbox editor.
data_access_role : int, optional
    Role for data access, default is QtCore.Qt.DisplayRole.
"""

        super().__init__(parent)
        self.item_dict = item_dict
        self._access_role = data_access_role
        # Note, the editor used in this delegate creates the unit prefix by
        # itself, therefore no handling for that is implemented.
        return

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
ScienDSpinBox
    A scientific spinbox editor for user interaction.
"""

        editor = ScienDSpinBox(parent=parent)
        if 'min' in self.item_dict:
            editor.setMinimum(self.item_dict['min'])
        if 'max' in self.item_dict:
            editor.setMaximum(self.item_dict['max'])
        if 'dec' in self.item_dict:
            editor.setDecimals(self.item_dict['dec'])
        if 'unit' in self.item_dict:
            editor.setSuffix(self.item_dict['unit'])
        editor.setGeometry(option.rect)
        editor.editingFinished.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self):
        return QtCore.QSize(90, 50)

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role)
        if not isinstance(data, float):
            data = self.item_dict['init_val']
        editor.blockSignals(True)
        editor.setValue(data)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : ScienDSpinBox
    The editor widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.value()
        # write the data to the model:
        model.setData(index, data, self._access_role)
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        widget = ScienDSpinBox()
        if 'dec' in self.item_dict:
            widget.setDecimals(self.item_dict['dec'])
        if 'unit' in self.item_dict:
            widget.setSuffix(self.item_dict['unit'])
        widget.setGeometry(r)
        widget.setValue(index.data(self._access_role))
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()


class ComboBoxItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, item_list, data_access_role=QtCore.Qt.DisplayRole,
                 size=QtCore.QSize(80, 50)):
        super().__init__(parent)
        self._item_list = item_list
        self._access_role = data_access_role
        self._size = size
        return

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
QtWidgets.QComboBox
    A combobox editor for user interaction.
"""

        widget = QtWidgets.QComboBox(parent)
        widget.addItems(self._item_list)
        widget.setGeometry(option.rect)
        widget.currentIndexChanged.connect(self.commitAndCloseEditor)
        return widget

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self):
        return self._size

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : QComboBox
    The combobox widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role)
        combo_index = editor.findText(data)
        editor.blockSignals(True)
        editor.setCurrentIndex(combo_index)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : QComboBox
    The combobox widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.currentText()
        model.setData(index, data, self._access_role)
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        widget = QtWidgets.QComboBox()
        widget.addItem(index.data(self._access_role))
        widget.setGeometry(r)
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()


class MultipleCheckboxItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, label_list, data_access_role=QtCore.Qt.DisplayRole):

        super().__init__(parent)
        self._label_list = list() if label_list is None else list(label_list)
        self._access_role = data_access_role
        return

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
MultipleCheckboxWidget
    A widget with multiple checkboxes for user interaction.
"""

        editor = MultipleCheckboxWidget(parent, self._label_list)
        editor.setData(index.data(self._access_role))
        editor.stateChanged.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self):
        widget = MultipleCheckboxWidget(None, self._label_list)
        return widget.sizeHint()

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : MultipleCheckboxWidget
    The widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role)
        editor.blockSignals(True)
        editor.setData(data)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : MultipleCheckboxWidget
    The widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.data()
        model.setData(index, data, self._access_role)
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        widget = MultipleCheckboxWidget(None, self._label_list)
        widget.setData(index.data(self._access_role))
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()


class AnalogParametersItemDelegate(QtWidgets.QStyledItemDelegate):
    """
    """
    editingFinished = QtCore.Signal()

    def __init__(self, parent, data_access_roles=None):
        super().__init__(parent)
        if data_access_roles is None:
            self._access_role = [QtCore.Qt.DisplayRole, QtCore.Qt.DisplayRole]
        else:
            self._access_role = data_access_roles

    def createEditor(self, parent, option, index):
        """
Create for the display and interaction with the user an editor.

Parameters
----------
parent : QtGui.QWidget
    The parent object, probably QTableView.
option : QtGui.QStyleOptionViewItemV4
    Style configuration options.
index : QtCore.QModelIndex
    Contains information about the selected current cell in the model.

Returns
-------
AnalogParametersWidget
    A widget for handling analog parameters for user interaction.
"""

        parameters = index.data(self._access_role[0]).params
        editor = AnalogParametersWidget(parent, parameters)
        editor.setData(index.data(self._access_role[1]))
        editor.editingFinished.connect(self.commitAndCloseEditor)
        return editor

    def commitAndCloseEditor(self):
        editor = self.sender()
        self.commitData.emit(editor)
        # self.closeEditor.emit(editor)
        self.editingFinished.emit()
        return

    def sizeHint(self, option, index):
        parameters = index.data(self._access_role[0]).params
        widget = AnalogParametersWidget(None, parameters)
        return widget.sizeHint()

    def setEditorData(self, editor, index):
        """
Set the display of the current value of the editor.

Parameters
----------
editor : AnalogParametersWidget
    The widget created in the createEditor function.
index : QtCore.QModelIndex
    Contains the current cell's data from the model.
"""

        data = index.data(self._access_role[1])
        editor.blockSignals(True)
        editor.setData(data)
        editor.blockSignals(False)
        return

    def setModelData(self, editor, model, index):
        """
Save the data of the editor to the model.

Parameters
----------
editor : AnalogParametersWidget
    The widget created in the createEditor function.
model : QtCore.QAbstractTableModel
    The data model object.
index : QtCore.QModelIndex
    Index of the current cell in the model.
"""

        data = editor.data()
        model.setData(index, data, self._access_role[1])
        return

    def paint(self, painter, option, index):
        painter.save()
        r = option.rect
        painter.translate(r.topLeft())
        parameters = index.data(self._access_role[0]).params
        widget = AnalogParametersWidget(None, parameters)
        widget.setData(index.data(self._access_role[1]))
        widget.render(painter, QtCore.QPoint(0, 0), painter.viewport())
        painter.restore()
