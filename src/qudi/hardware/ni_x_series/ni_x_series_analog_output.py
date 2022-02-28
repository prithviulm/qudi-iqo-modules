# -*- coding: utf-8 -*-

"""
This file contains the qudi hardware module to use a National Instruments X-series card as mixed
signal input data streamer.

Qudi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Qudi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Qudi. If not, see <http://www.gnu.org/licenses/>.

Copyright (c) the Qudi Developers. See the COPYRIGHT.txt file at the
top-level directory of this distribution and at <https://github.com/Ulm-IQO/qudi/>
"""

import ctypes
from typing_extensions import final
import warnings

import numpy as np
import nidaqmx as ni
from nidaqmx._lib import lib_importer  # Due to NIDAQmx C-API bug needed to bypass property getter
from nidaqmx.stream_readers import AnalogMultiChannelReader, CounterReader
from nidaqmx.stream_writers import AnalogSingleChannelWriter

from qudi.util.mutex import RecursiveMutex
from qudi.core.configoption import ConfigOption
from qudi.core.statusvariable import StatusVar
from qudi.util.helpers import natural_sort

from qudi.interface.process_control_interface import ProcessControlConstraints
from qudi.interface.process_control_interface import ProcessSetpointInterface


class NIXSeriesAnalogOutput(ProcessSetpointInterface):
    """ A dummy class to emulate a process control device (setpoints and process values)

    Example config for copy-paste:

    nicard_6343_ao:
        module.Class: 'ni_x_series.ni_x_series_in_streamer.NIXSeriesAnalogOutput'
        device_name: 'Dev1'

        setpoint_channels:
            ao0:
                unit: 'V'
                limits: [-10.0, 10.0]
                keep_value: True
            ao1:
                unit: 'V'
                limits: [-10.0, 10.0]
                keep_value: True
            ao2:
                unit: 'V'
                limits: [-10.0, 10.0]
                keep_value: True
            ao3:
                unit: 'V'
                limits: [-10.0, 10.0]   
                keep_value: True         
    """
    _device_name = ConfigOption(name='device_name', default='Dev1', missing='warn')

    _setpoint_channels = ConfigOption(
        name='setpoint_channels',
        default={
                'ao0': {'unit': 'V', 'limits': (-10.0, 10.0), 'dtype': float, 'keep_value': False},
                'ao1': {'unit': 'V', 'limits': (-10.0, 10.0), 'dtype': float, 'keep_value': False},
                'ao2': {'unit': 'V', 'limits': (-10.0, 10.0), 'dtype': float, 'keep_value': False},
                'ao3': {'unit': 'V', 'limits': (-10.0, 10.0), 'dtype': float, 'keep_value': False}
                },
        missing='info'
    )
    _test = ConfigOption(name='test')

    _setpoints = StatusVar(name='current_setpoints', default=dict())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_lock = RecursiveMutex()

        self._system = None
        self._device_handle = None
        self._ao_ch_names = list()
        self._ao_task_handles = dict()
        self._ao_writer_handles = dict()
        self._keep_values = None
        
        self._is_active = False
        self.__constraints = None

    def on_activate(self):
        """
            Starts up the NI-card and performs sanity checks.
        """
        # TODO Need to check the value range of config that it does not exceed ni limits
        # Check if device is connected and set device to use
        device_names = ni.system.System().devices.device_names
        if self._device_name.lower() not in set(dev.lower() for dev in device_names):
            raise ValueError(
                f'Device name "{self._device_name}" not found in list of connected devices: '
                f'{device_names}\nActivation of NIXSeriesAnalogOutput failed!'
            )
        for device_name in device_names:
            if device_name.lower() == self._device_name.lower():
                self._device_name = device_name
                break
        self._device_handle = ni.system.Device(self._device_name)

        # Check if given ao channel names from the cfg are a subset of the available ao channel names
        self.__avlbl_ao_ch_names = tuple(
            term.rsplit('/', 1)[-1].lower() for term in self._device_handle.ao_physical_chans.channel_names)
        ao_ch_names_set = set(self._extract_ch_name(ao_ch_name) for ao_ch_name in self._setpoint_channels)
        
        invalid_sources = ao_ch_names_set.difference(set(self.__avlbl_ao_ch_names))
        if invalid_sources:
            self.log.error('Invalid analog source channels encountered. Following sources will '
                            'be ignored:\n  {0}\nValid analog input channels are:\n  {1}'
                            ''.format(', '.join(natural_sort(invalid_sources)),
                                        ', '.join(self.__avlbl_ao_ch_names)))
        self._ao_ch_names = natural_sort(ao_ch_names_set.difference(invalid_sources))

        if not self._ao_ch_names:
            raise ValueError(
                'No valid analog ouput sources defined in config. Activation of '
                'NIXSeriesAnalogOutput failed!'
            )
        
        # Initialization of hardware constraints defined in the config file
        units = {ch: d['unit'] for ch, d in self._setpoint_channels.items() if 'unit' in d}
        limits = {ch: d['limits'] for ch, d in self._setpoint_channels.items() if 'limits' in d}
        dtypes = {ch: d['dtype'] for ch, d in self._setpoint_channels.items() if 'dtype' in d}
        self._keep_values = {ch: d['keep_value'] for ch, d in self._setpoint_channels.items() if 'keep_value' in d}

        self.__constraints = ProcessControlConstraints(
            setpoint_channels=tuple(self._setpoint_channels),
            units=units,
            limits=limits,
            dtypes=dtypes
        )
        
        if not self._setpoints:
            self._setpoints = {ch: min(max(lim[0], 0), lim[1]) for ch, lim in
                            self.__constraints.channel_limits.items() if
                            ch in self._setpoint_channels}

    def on_deactivate(self):
        if self._is_active:
            for ao_ch_name in self._ao_ch_names:
                self.terminate_ao_task(ao_ch_name)

    @property
    def constraints(self):
        """ Read-Only property holding the constraints for this hardware module.
        See class ProcessControlConstraints for more details.

        @return ProcessControlConstraints: Hardware constraints
        """
        return self.__constraints

    @property
    def is_active(self):
        """ Current activity state.
        State is bool type and refers to active (True) and inactive (False).

        @return bool: Activity state (active: True, inactive: False)
        """
        with self._thread_lock:
            return self._is_active

    @is_active.setter
    def is_active(self, active):
        """ Set activity state.
        State is bool type and refers to active (True) and inactive (False).

        @param bool active: Activity state to set (active: True, inactive: False)
        """
        self.set_activity_state(active)

    @property
    def setpoints(self):
        """ The current setpoints for all channels.

        @return dict: Currently set target values (values) for all channels (keys)
        """
        with self._thread_lock:
            return self._setpoints.copy()

    @setpoints.setter
    def setpoints(self, values):
        """ Set the setpoints for all channels at once.

        @param dict values: Target values (values) to set for all channels (keys)
        """
        assert self._is_active, 'Please activate first!'

        assert set(values).issubset(self._setpoints), \
            f'Invalid setpoint channels encountered. Valid channels are: {set(self._setpoints)}'
        assert all(self.__constraints.channel_value_in_range(v, ch)[0] for ch, v in
                   values.items()), 'One or more setpoints out of allowed value bounds'
        
        with self._thread_lock:
            for ch, v in values.items():
                self.set_setpoint(ch, v)

    def set_activity_state(self, active):
        """ Set activity state. State is bool type and refers to active (True) and inactive (False).

        @param bool active: Activity state to set (active: True, inactive: False)
        """
        assert isinstance(active, bool), '<is_active> flag must be bool type'
        with self._thread_lock:
            if active != self._is_active:
                if active and self.module_state() != 'locked':
                    for ao_ch_name in self._ao_ch_names:
                        ao_task = ni.Task(ao_ch_name)
                        ao_phys_ch = f"/{self._device_name}/{ao_ch_name}"
                        ao_task.ao_channels.add_ao_voltage_chan(
                                                                physical_channel=ao_phys_ch,
                                                                min_val=self.__constraints.channel_limits[ao_ch_name][0], 
                                                                max_val=self.__constraints.channel_limits[ao_ch_name][1]
                                                                )
                        self._ao_task_handles[ao_ch_name] = ao_task

                    self.module_state.lock()
                elif not active and self.module_state() == 'locked':
                    for ao_ch_name in self._ao_ch_names:
                        self.terminate_ao_task(ao_ch_name)
                    self.module_state.unlock()
                self._is_active = active

    def set_setpoint(self, channel, value):
        """ Set new setpoint for a single channel.

        @param str channel: Channel to set
        @param float|int value: Setpoint value to set
        """
        
        assert self._is_active, 'Please activate first!'
        
        assert channel in self._setpoints, \
            f'Invalid setpoint channel "{channel}" encountered. Valid channels are: ' \
            f'{set(self._setpoints)}'
        assert self.__constraints.channel_value_in_range(value, channel)[0], \
            'Setpoint out of allowed value bounds'
        with self._thread_lock:
            self._setpoints[channel] = self.__constraints.channel_dtypes[channel](value)
            self._ao_task_handles[channel].write(self._setpoints[channel])

    def get_setpoint(self, channel):
        """ Get current setpoint for a single channel.

        @param str channel: Channel to get the setpoint for
        @return float|int: The current setpoint for <channel>
        """
        assert channel in self._setpoints, f'Invalid setpoint channel "{channel}" encountered.' \
                                           f' Valid channels are: {set(self._setpoints)}'
        with self._thread_lock:
            return self._setpoints[channel]

    def terminate_ao_task(self, ao_ch_name):
        """
            Reset analog output to 0 if keep_value flag is False
        """
        if not self._keep_values[ao_ch_name]:
            self.set_setpoint(ao_ch_name, 0)    

        try:
            if not self._ao_task_handles[ao_ch_name].is_task_done():
                self._ao_task_handles[ao_ch_name].stop()
            self._ao_task_handles[ao_ch_name].close()
        except ni.DaqError:
            self.log.exception('Error while trying to terminate analog output task.')
            err = -1
        finally:
            del self._ao_task_handles[ao_ch_name]
    
    @staticmethod
    def _extract_ch_name(ch_str):
        """
        Helper function to extract the bare terminal name from a string and strip it of the device
        name and dashes.
        Will return the terminal name in lower case.
        @param str term_str: The str to extract the terminal name from
        @return str: The terminal name in lower case
        """
        ch_name = ch_str.strip('/').lower()
        if 'dev' in ch_name:
            ch_name = ch_name.split('/', 1)[-1]
        return ch_name