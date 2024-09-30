# -*- coding: utf-8 -*-

"""
This file contains the Qudi hardware interface for pulsing devices.

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

from qudi.util.paths import get_home_dir
import numpy as np
import ctypes
import os

import PyDAQmx as daq

from qudi.core.module import Base
from qudi.core.configoption import ConfigOption
from qudi.interface.pulser_interface import PulserInterface
from collections import OrderedDict


class NationalInstrumentsPulser(Base, PulserInterface):
    """Pulse generator using NI-DAQmx

    Example config for copy-paste:

    ni_pulser:
        module.Class: 'national_instruments_pulser.NationalInstrumentsPulser'
        options:
            device: 'Dev0'
            #pulsed_file_dir: 'C:\\Software\\qudi_pulsed_files' # optional, path

    """

    device = ConfigOption("device", default="Dev0", missing="warn")

    def on_activate(self):
        """Activate module"""
        self.log.warning(
            "This module has not been tested on the new qudi core."
            "Use with caution and contribute bug fixed back, please."
        )

        config = self.getConfiguration()
        if "pulsed_file_dir" in config.keys():
            self.pulsed_file_dir = config["pulsed_file_dir"]

            if not os.path.exists(self.pulsed_file_dir):
                homedir = get_home_dir()
                self.pulsed_file_dir = os.path.join(homedir, "pulsed_files")
                self.log.warning(
                    'The directory defined in parameter "pulsed_file_dir" in the config for '
                    "SequenceGeneratorLogic class does not exist!\nThe default home directory\n"
                    "{0}\n will be taken instead.".format(self.pulsed_file_dir)
                )
        else:
            homedir = get_home_dir()
            self.pulsed_file_dir = os.path.join(homedir, "pulsed_files")
            self.log.warning(
                'No parameter "pulsed_file_dir" was specified in the config for NIPulser '
                "as directory for the pulsed files!\nThe default home directory\n{0}\n"
                "will be taken instead.".format(self.pulsed_file_dir)
            )

        self.host_waveform_directory = self._get_dir_for_name("sampled_hardware_files")

        self.pulser_task = daq.TaskHandle()
        daq.DAQmxCreateTask("NI Pulser", daq.byref(self.pulser_task))

        self.current_status = -1
        self.current_loaded_asset = None
        self.init_constraints()

        # analog voltage
        self.min_volts = -10
        self.max_volts = 10
        self.sample_rate = 1000

        self.a_names = []
        self.d_names = []

        self.set_active_channels(
            {k: True for k in self.constraints["activation_config"]["analog_only"]}
        )
        # self.sample_rate = self.get_sample_rate()

    def on_deactivate(self):
        """Deactivate module"""
        self.close_pulser_task()

    def init_constraints(self):
        """Build a pulser constraints dictionary with information from the NI card."""
        device = self.device
        constraints = {}
        ch_map = OrderedDict()

        n = 2048
        ao_max_freq = daq.float64()
        ao_min_freq = daq.float64()
        ao_physical_chans = ctypes.create_string_buffer(n)
        ao_voltage_ranges = np.zeros(16, dtype=np.float64)
        ao_clock_support = daq.bool32()
        do_max_freq = daq.float64()
        do_lines = ctypes.create_string_buffer(n)
        do_ports = ctypes.create_string_buffer(n)
        product_dev_type = ctypes.create_string_buffer(n)
        product_cat = daq.int32()
        serial_num = daq.uInt32()
        product_num = daq.uInt32()

        daq.DAQmxGetDevAOMinRate(device, daq.byref(ao_min_freq))
        self.log.debug("Analog min freq: {0}".format(ao_min_freq.value))
        daq.DAQmxGetDevAOMaxRate(device, daq.byref(ao_max_freq))
        self.log.debug("Analog max freq: {0}".format(ao_max_freq.value))
        daq.DAQmxGetDevAOSampClkSupported(device, daq.byref(ao_clock_support))
        self.log.debug("Analog supports clock: {0}".format(ao_clock_support.value))
        daq.DAQmxGetDevAOPhysicalChans(device, ao_physical_chans, n)
        analog_channels = str(ao_physical_chans.value, encoding="utf-8").split(", ")
        self.log.debug("Analog channels: {0}".format(analog_channels))
        daq.DAQmxGetDevAOVoltageRngs(
            device,
            ao_voltage_ranges.ctypes.data_as(ctypes.POINTER(ctypes.c_double)),
            len(ao_voltage_ranges),
        )
        self.log.debug("Analog voltage range: {0}".format(ao_voltage_ranges[0:2]))

        daq.DAQmxGetDevDOMaxRate(self.device, daq.byref(do_max_freq))
        self.log.debug("Digital max freq: {0}".format(do_max_freq.value))
        daq.DAQmxGetDevDOLines(device, do_lines, n)
        digital_channels = str(do_lines.value, encoding="utf-8").split(", ")
        self.log.debug("Digital channels: {0}".format(digital_channels))
        daq.DAQmxGetDevDOPorts(device, do_ports, n)
        digital_bundles = str(do_ports.value, encoding="utf-8").split(", ")
        self.log.debug("Digital ports: {0}".format(digital_bundles))

        daq.DAQmxGetDevSerialNum(device, daq.byref(serial_num))
        self.log.debug("Card serial number: {0}".format(serial_num.value))
        daq.DAQmxGetDevProductNum(device, daq.byref(product_num))
        self.log.debug("Product number: {0}".format(product_num.value))
        daq.DAQmxGetDevProductType(device, product_dev_type, n)
        product = str(product_dev_type.value, encoding="utf-8")
        self.log.debug("Product name: {0}".format(product))
        daq.DAQmxGetDevProductCategory(device, daq.byref(product_cat))
        self.log.debug(product_cat.value)

        for n, ch in enumerate(analog_channels):
            ch_map["a_ch{0:d}".format(n + 1)] = ch

        for n, ch in enumerate(digital_channels):
            ch_map["d_ch{0:d}".format(n + 1)] = ch

        constraints["sample_rate"] = {
            "min": ao_min_freq.value,
            "max": ao_max_freq.value,
            "step": 0.0,
            "unit": "Samples/s",
        }

        # The file formats are hardware specific. The sequence_generator_logic will need this
        # information to choose the proper output format for waveform and sequence files.
        constraints["waveform_format"] = "ndarray"
        constraints["sequence_format"] = None

        # the stepsize will be determined by the DAC in combination with the
        # maximal output amplitude (in Vpp):
        constraints["a_ch_amplitude"] = {
            "min": 0,
            "max": ao_voltage_ranges[1],
            "step": 0.0,
            "unit": "Vpp",
        }
        constraints["a_ch_offset"] = {
            "min": ao_voltage_ranges[0],
            "max": ao_voltage_ranges[1],
            "step": 0.0,
            "unit": "V",
        }
        constraints["d_ch_low"] = {"min": 0.0, "max": 0.0, "step": 0.0, "unit": "V"}
        constraints["d_ch_high"] = {"min": 5.0, "max": 5.0, "step": 0.0, "unit": "V"}
        constraints["sampled_file_length"] = {
            "min": 2,
            "max": 1e12,
            "step": 0,
            "unit": "Samples",
        }
        constraints["digital_bin_num"] = {"min": 2, "max": 1e12, "step": 0, "unit": "#"}
        constraints["waveform_num"] = {"min": 1, "max": 1, "step": 0, "unit": "#"}
        constraints["sequence_num"] = {"min": 0, "max": 0, "step": 0, "unit": "#"}
        constraints["subsequence_num"] = {"min": 0, "max": 0, "step": 0, "unit": "#"}

        # If sequencer mode is enable than sequence_param should be not just an
        # empty dictionary.
        sequence_param = OrderedDict()
        constraints["sequence_param"] = sequence_param

        activation_config = OrderedDict()
        activation_config["analog_only"] = [
            k for k in ch_map.keys() if k.startswith("a")
        ]
        activation_config["digital_only"] = [
            k for k in ch_map.keys() if k.startswith("d")
        ]
        activation_config["stuff"] = ["a_ch4", "d_ch1", "d_ch2", "d_ch3", "d_ch4"]
        constraints["activation_config"] = activation_config

        self.channel_map = ch_map
        self.constraints = constraints

    def configure_pulser_task(self):
        """
        Clear pulser task and set to current settings.

        Returns
        -------
        None
        """

        a_channels = [self.channel_map[k] for k in self.a_names]
        d_channels = [self.channel_map[k] for k in self.d_names]

        # clear task
        daq.DAQmxClearTask(self.pulser_task)

        # add channels
        if len(a_channels) > 0:
            daq.DAQmxCreateAOVoltageChan(
                self.pulser_task,
                ", ".join(a_channels),
                ", ".join(self.a_names),
                self.min_volts,
                self.max_volts,
                daq.DAQmx_Val_Volts,
                "",
            )

        if len(d_channels) > 0:
            daq.DAQmxCreateDOChan(
                self.pulser_task,
                ", ".join(d_channels),
                ", ".join(self.d_names),
                daq.DAQmx_Val_ChanForAllLines,
            )

            # set sampling frequency
            daq.DAQmxCfgSampClkTiming(
                self.pulser_task,
                "OnboardClock",
                self.sample_rate,
                daq.DAQmx_Val_Rising,
                daq.DAQmx_Val_ContSamps,
                10 * self.sample_rate,
            )

        # write assets

    def close_pulser_task(self):
        """
        Clear tasks.

        Returns
        -------
        int
            Error code (0: OK, -1: error)
        """

        retval = 0
        try:
            # stop the task
            daq.DAQmxStopTask(self.pulser_task)
        except:
            self.log.exception("Error while closing NI pulser.")
            retval = -1
        try:
            # clear the task
            daq.DAQmxClearTask(self.pulser_task)
        except:
            self.log.exception("Error while clearing NI pulser.")
            retval = -1
        return retval

    def get_constraints(self):
        """
        Retrieve the hardware constraints from the pulsing device.

        Returns
        -------
        dict
            Dictionary with constraints for the sequence generation and GUI.
        """

        return self.constraints

    def pulser_on(self):
        """
        Switches the pulsing device on.

        Returns
        -------
        int
            Error code (0: OK, -1: error)
        """

        try:
            daq.DAQmxStartTask(self.pulser_task)
        except:
            self.log.exception("Error starting NI pulser.")
            return -1
        return 0

    def pulser_off(self):
        """
        Switches the pulsing device off.

        Returns
        -------
        int
            Error code (0: OK, -1: error)
        """

        try:
            daq.DAQmxStopTask(self.pulser_task)
        except:
            self.log.exception("Error stopping NI pulser.")
            return -1
        return 0

    def upload_asset(self, asset_name=None):
        """
        Upload an already hardware conform file to the device mass memory.
        Also loads these files into the device workspace if present.
        Does NOT load waveforms/sequences/patterns into channels.

        Parameters
        ----------
        asset_name : str, optional
            Name of the ensemble/sequence to be uploaded.

        Returns
        -------
        int
            Error code (0: OK, -1: error)

        Notes
        -----
        This method has no effect when using pulser hardware without own mass memory
        (i.e., PulseBlaster, FPGA).
        """

        self.log.debug(
            'NI pulser has no own storage capability.\n"upload_asset" call ignored.'
        )
        return 0

    def load_asset(self, asset_name, load_dict=None):
        """
        Loads a sequence or waveform to the specified channel of the pulsing device.
        For devices that have a workspace (i.e., AWG), this will load the asset from the
        device workspace into the channel. For a device without mass memory, this will
        transfer the waveform/sequence/pattern data directly to the device so that it
        is ready to play.

        Parameters
        ----------
        asset_name : str
            The name of the asset to be loaded.
        load_dict : dict, optional
            A dictionary with keys being one of the available channel numbers
            and items being the name of the already sampled waveform/sequence
            files. If not provided, channel association is invoked from the
            file name (e.g., the appendix _ch1, _ch2, etc.)

        Returns
        -------
        int
            Error code (0: OK, -1: error)
        """

        # ignore if no asset_name is given
        if asset_name is None:
            self.log.warning('"load_asset" called with asset_name = None.')
            return 0

        # check if asset exists
        saved_assets = self.get_saved_asset_names()
        if asset_name not in saved_assets:
            self.log.error(
                'No asset with name "{0}" found for NI pulser.\n'
                '"load_asset" call ignored.'.format(asset_name)
            )
            return -1

        # get samples from file
        filepath = os.path.join(self.host_waveform_directory, asset_name + ".npz")
        self.samples = np.load(filepath)

        self.current_loaded_asset = asset_name

    def get_loaded_asset(self):
        """
        Retrieve the currently loaded asset name of the device.

        Returns
        -------
        str
            Name of the current asset ready to play. (no filename)
        """

        return self.current_loaded_asset

    def clear_all(self):
        """
        Clears all loaded waveforms from the pulse generator's RAM/workspace.

        Returns
        -------
        int
            Error code (0: OK, -1: error)
        """

        pass

    def get_status(self):
        """
        Retrieves the status of the pulsing hardware.

        Returns
        -------
        tuple
            Tuple containing:
            - int: Current status value.
            - dict: Status description for all possible status variables of
              the pulse generator hardware.

        Notes
        -----
        The status values are:
            - -1: Failed Request or Communication.
            - 0: Device has stopped, but can receive commands.
            - 1: Device is active and running.
        """

        status_dict = {
            -1: "Failed Request or Communication",
            0: "Device has stopped, but can receive commands.",
            1: "Device is active and running.",
        }
        task_done = daq.bool32
        try:
            daq.DAQmxIsTaskDone(self.pulser_task, daq.byref(task_done))
            current_status = 0 if task_done.value else 1
        except:
            self.log.exception("Error while getting pulser state.")
            current_status = -1
        return current_status, status_dict

    def get_sample_rate(self):
        """
        Get the sample rate of the pulse generator hardware.

        Returns
        -------
        float
            The current sample rate of the device (in Hz).
        """

        rate = daq.float64()
        daq.DAQmxGetSampClkRate(self.pulser_task, daq.byref(rate))
        return rate.value

    def set_sample_rate(self, sample_rate):
        """
        Set the sample rate of the pulse generator hardware.

        Parameters
        ----------
        sample_rate : float
            The sampling rate to be set (in Hz).

        Returns
        -------
        float
            The sample rate returned from the device (in Hz).

        Notes
        -----
        After setting the sampling rate of the device, use the actual set return value for further processing.
        """

        task = self.pulser_task
        source = "OnboardClock"
        rate = sample_rate
        edge = daq.DAQmx_Val_Rising
        mode = daq.DAQmx_Val_ContSamps
        samples = 10000
        daq.DAQmxCfgSampClkTiming(task, source, rate, edge, mode, samples)
        self.sample_rate = self.get_sample_rate()
        return self.sample_rate

    def get_analog_level(self, amplitude=None, offset=None):
        """
        Retrieve the analog amplitude and offset of the provided channels.

        Parameters
        ----------
        amplitude : list, optional
            If specified, the amplitude value (in Volt peak-to-peak, i.e. the full amplitude)
            of a specific channel.
        offset : list, optional
            If specified, the offset value (in Volts) of a specific channel.

        Returns
        -------
        tuple of dict
            Two dicts, with keys being the channel descriptor string (i.e. 'a_ch1') and items
            being the values for those channels. Amplitude is always denoted in Volt-peak-to-peak
            and Offset in Volts.

        Notes
        -----
        Do not return a saved amplitude and/or offset value but instead retrieve the current
        amplitude and/or offset directly from the device.

        If nothing (or None) is passed, then the levels of all channels will be returned.
        If no analog channels are present in the device, empty dicts are returned.

        Examples
        --------
        >>> amplitude = ['a_ch1', 'a_ch4']
        >>> offset = None
        >>> get_analog_level(amplitude, offset)
        ({'a_ch1': -0.5, 'a_ch4': 2.0}, {'a_ch1': 0.0, 'a_ch2': 0.0, 'a_ch3': 1.0, 'a_ch4': 0.0})

        The major difference to digital signals is that analog signals are always oscillating
        or changing signals, otherwise, you can use digital output. In contrast to digital output
        levels, analog output levels are defined by an amplitude (total signal span, denoted in
        Voltage peak-to-peak) and an offset (a value around which the signal oscillates, denoted by
        an absolute voltage).

        There is no bijective correspondence between (amplitude, offset) and (value high, value low).
        """

        amp_dict = {}
        off_dict = {}

        return amp_dict, off_dict

    def set_analog_level(self, amplitude=None, offset=None):
        """
        Set amplitude and/or offset value of the provided analog channel(s).

        Parameters
        ----------
        amplitude : dict, optional
            Dictionary with keys being the channel descriptor string (i.e., 'a_ch1', 'a_ch2') and
            values being the amplitude (Volt peak-to-peak, i.e., the full amplitude) for the desired
            channel.
        offset : dict, optional
            Dictionary with keys being the channel descriptor string (i.e., 'a_ch1', 'a_ch2') and
            values being the offset (in absolute Volts) for the desired channel.

        Returns
        -------
        tuple of dict
            Tuple of two dicts with the actual set values for amplitude and offset for ALL channels.

        Notes
        -----
        If nothing is passed, the command will return the current amplitudes/offsets.

        After setting the amplitude and/or offset values of the device, use the actual set return
        values for further processing.

        The major difference to digital signals is that analog signals are always oscillating or
        changing signals, otherwise, digital output can be used. In contrast to digital output
        levels, analog output levels are defined by an amplitude (total signal span, denoted in
        Voltage peak-to-peak) and an offset (a value around which the signal oscillates, denoted by
        an absolute voltage).

        There is no bijective correspondence between (amplitude, offset) and (value high, value low).
        """

        return self.get_analog_level(amplitude, offset)

    def get_digital_level(self, low=None, high=None):
        """
        Retrieve the digital low and high level of the provided/all channels.

        Parameters
        ----------
        low : list, optional
            If specified, retrieves the low value (in Volts) of a specific channel.
        high : list, optional
            If specified, retrieves the high value (in Volts) of a specific channel.

        Returns
        -------
        tuple of dict
            Tuple of two dicts, with keys being the channel descriptor strings (i.e., 'd_ch1', 'd_ch2')
            and items being the low and high values for those channels. Both low and high values
            are denoted in volts.

        Notes
        -----
        Do not return a saved low and/or high value but instead retrieve the current low and/or high value
        directly from the device.

        If nothing (or None) is passed, then the levels of all channels are returned. If no digital
        channels are present, returns just an empty dict.

        Examples
        --------
        >>> low = ['d_ch1', 'd_ch4']
        >>> get_digital_level(low)
        ({'d_ch1': -0.5, 'd_ch4': 2.0}, {'d_ch1': 1.0, 'd_ch2': 1.0, 'd_ch3': 1.0, 'd_ch4': 4.0})

        The major difference to analog signals is that digital signals are either ON or OFF,
        whereas analog channels have a varying amplitude range. In contrast to analog output levels,
        digital output levels are defined by a voltage, which corresponds to the ON status
        and a voltage which corresponds to the OFF status (both denoted in absolute voltage).

        There is no bijective correspondence between (amplitude, offset) and (value high, value low).
        """

        # digital levels not settable on NI card
        return self.get_digital_level(low, high)

    def get_active_channels(self, ch=None):
        """
        Get the active channels of the pulse generator hardware.

        Parameters
        ----------
        ch : list, optional
            List of specific analog or digital channels to query without obtaining all the channels.

        Returns
        -------
        dict
            A dictionary where keys denote the channel string and items are boolean expressions indicating
            whether the channel is active or not.

        Examples
        --------
        >>> ch = ['a_ch2', 'd_ch2', 'a_ch1', 'd_ch5', 'd_ch1']
        >>> get_active_channels(ch)
        {'a_ch2': True, 'd_ch2': False, 'a_ch1': False, 'd_ch5': True, 'd_ch1': False}

        If no parameter (or None) is passed, the states of all channels will be returned.
        """

        buffer_size = 2048
        buf = ctypes.create_string_buffer(buffer_size)
        daq.DAQmxGetTaskChannels(self.pulser_task, buf, buffer_size)
        ni_ch = str(buf.value, encoding="utf-8").split(", ")

        if ch is None:
            return {k: k in ni_ch for k, v in self.channel_map.items()}
        else:
            return {k: k in ni_ch for k in ch}

    def set_active_channels(self, ch=None):
        """
        Set the active/inactive channels for the pulse generator hardware.
        The state of ALL available analog and digital channels will be returned (True: active, False: inactive).
        The actually set and returned channel activation must be part of the available activation_configs in the constraints.
        You can also activate/deactivate subsets of available channels, but the resulting activation_config must still be valid according to the constraints.
        If the resulting set of active channels cannot be found in the available activation_configs, the channel states must remain unchanged.

        Parameters
        ----------
        ch : dict, optional
            Dictionary with keys being the analog or digital string generic names for the channels
            (i.e., 'd_ch1', 'a_ch2') with values being a boolean expression (True: Activate channel, False: Deactivate channel).

        Returns
        -------
        dict
            Dictionary with the actual set values for ALL active analog and digital channels.

        Notes
        -----
        If nothing is passed, the command will simply return the unchanged current state.

        After setting the active channels of the device, use the returned dictionary for further processing.

        Examples
        --------
        >>> ch = {'a_ch2': True, 'd_ch1': False, 'd_ch3': True, 'd_ch4': True}
        >>> set_active_channels(ch)
        # This activates analog channel 2, digital channels 3 and 4, and deactivates digital channel 1.
        # All other available channels will remain unchanged.
        """

        self.a_names = [k for k, v in ch.items() if k.startswith("a") and v]
        self.a_names.sort()

        self.d_names = [k for k, v in ch.items() if k.startswith("d") and v]
        self.d_names.sort()

        # apply changed channels
        self.configure_pulser_task()
        return self.get_active_channels()

    def get_uploaded_asset_names(self):
        """
        Retrieve the names of all uploaded assets on the device.

        Returns
        -------
        list
            List of all uploaded asset name strings in the current device directory.
            This is not a list of the file names.

        Notes
        -----
        Unused for pulse generators without sequence storage capability (e.g., PulseBlaster, FPGA).
        """

        # no storage
        return []

    def get_saved_asset_names(self):
        """
        Retrieve the names of all uploaded assets on the device.

        Returns
        -------
        list
            List of all uploaded asset name strings in the current device directory.
            This is not a list of the file names.

        Notes
        -----
        Unused for pulse generators without sequence storage capability (e.g., PulseBlaster, FPGA).
        """

        file_list = self._get_filenames_on_host()
        saved_assets = []
        for filename in file_list:
            if filename.endswith(".npz"):
                asset_name = filename.rsplit(".", 1)[0]
                if asset_name not in saved_assets:
                    saved_assets.append(asset_name)
        return saved_assets

    def delete_asset(self, asset_name):
        """
        Delete all files associated with an asset with the passed asset_name from the device
        memory (mass storage as well as AWG workspace/channels).

        Parameters
        ----------
        asset_name : str
            The name of the asset to be deleted. Optionally, a list of asset names can be passed.

        Returns
        -------
        list
            A list of strings representing the files that were deleted.

        Notes
        -----
        Unused for pulse generators without sequence storage capability (e.g., PulseBlaster, FPGA).
        """

        # no storage
        return 0

    def set_asset_dir_on_device(self, dir_path):
        """
        Change the directory where the assets are stored on the device.

        Parameters
        ----------
        dir_path : str
            The target directory.

        Returns
        -------
        int
            Error code (0: OK, -1: error).

        Notes
        -----
        Unused for pulse generators without changeable file structure (e.g., PulseBlaster, FPGA).
        """

        # no storage
        return 0

    def get_asset_dir_on_device(self):
        """
        Ask for the directory where the hardware-conform files are stored on the device.

        Returns
        -------
        str
            The current file directory.

        Notes
        -----
        Unused for pulse generators without changeable file structure (e.g., PulseBlaster, FPGA).
        """

        # no storage
        return ""

    def get_interleave(self):
        """
        Check whether Interleave is ON or OFF in AWG.

        Returns
        -------
        bool
            True if Interleave is ON, False if OFF.

        Notes
        -----
        Will always return False for pulse generator hardware without interleave.
        """

        return False

    def set_interleave(self, state=False):
        """
        Turn the interleave of an AWG on or off.

        Parameters
        ----------
        state : bool
            The state to set the interleave to (True: ON, False: OFF).

        Returns
        -------
        bool
            The actual interleave status (True: ON, False: OFF).

        Notes
        -----
        After setting the interleave of the device, retrieve the interleave again and use that information for further processing.

        Unused for pulse generator hardware other than an AWG.
        """

        return False

    def tell(self, command):
        """
        Send a command string to the device.

        Parameters
        ----------
        command : str
            String containing the command.

        Returns
        -------
        int
            Error code (0: OK, -1: error).
        """

        return 0

    def ask(self, question):
        """
        Ask the device a 'question' and receive and return an answer from it.

        Parameters
        ----------
        question : str
            String containing the command.

        Returns
        -------
        str
            The answer of the device to the 'question' as a string.
        """

        return ""

    def reset(self):
        """
        Reset the device.

        Returns
        -------
        int
            Error code (0: OK, -1: error).
        """

        try:
            daq.DAQmxResetDevice(self.device)
        except:
            self.log.exception("Could not reset NI device {0}".format(self.device))
            return -1
        return 0

    def has_sequence_mode(self):
        """
        Ask the pulse generator whether sequence mode exists.

        Returns
        -------
        bool
            True if sequence mode exists, False otherwise.
        """

        return False

    def _get_dir_for_name(self, name):
        """
        Get the path to the pulsed sub-directory 'name'.

        Parameters
        ----------
        name : str
            The name of the folder.

        Returns
        -------
        str
            The absolute path to the directory with the folder 'name'.
        """

        path = os.path.join(self.pulsed_file_dir, name)
        if not os.path.exists(path):
            os.makedirs(os.path.abspath(path))
        return os.path.abspath(path)

    def _get_filenames_on_host(self):
        """
        Get the full filenames of all assets saved on the host PC.

        Returns
        -------
        list
            The full filenames of all assets saved on the host PC.
        """

        filename_list = [
            f for f in os.listdir(self.host_waveform_directory) if f.endswith(".npz")
        ]
        return filename_list
    

    