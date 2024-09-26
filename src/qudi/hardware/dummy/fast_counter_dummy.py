# -*- coding: utf-8 -*-

"""
This file contains the Qudi hardware dummy for fast counting devices.

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

import time
import os
import numpy as np

from qudi.core.configoption import ConfigOption
from qudi.interface.fast_counter_interface import FastCounterInterface


class FastCounterDummy(FastCounterInterface):
    """ Implementation of the FastCounter interface methods for a dummy usage.

    Example config for copy-paste:

    fastcounter_dummy:
        module.Class: 'fast_counter_dummy.FastCounterDummy'
        options:
            gated: False
            #load_trace: None # path to the saved dummy trace

    """

    # config option
    _gated = ConfigOption('gated', False, missing='warn')
    trace_path = ConfigOption('load_trace', None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.trace_path is None:
            self.trace_path = os.path.abspath(os.path.join(__file__,
                                                           '..',
                                                           'FastComTec_demo_timetrace.asc'))
            self.log.debug(f"Loading dummy fastcounter trace: {self.trace_path}")

    def on_activate(self):
        """ Initialisation performed during activation of the module.
        """
        self.statusvar = 0
        self._binwidth = 1
        self._gate_length_bins = 8192
        return

    def on_deactivate(self):
        """ Deinitialisation performed during deactivation of the module.
        """
        self.statusvar = -1
        return

    def get_constraints(self):
        """ Retrieve the hardware constrains from the Fast counting device.

        @return dict: dict with keys being the constraint names as string and
                      items are the definition for the constaints.

         The keys of the returned dictionary are the str name for the constraints
        (which are set in this method).

                    NO OTHER KEYS SHOULD BE INVENTED!

        If you are not sure about the meaning, look in other hardware files to
        get an impression. If still additional constraints are needed, then they
        have to be added to all files containing this interface.

        The items of the keys are again dictionaries which have the generic
        dictionary form:
            {'min': <value>,
             'max': <value>,
             'step': <value>,
             'unit': '<value>'}

        Only the key 'hardware_binwidth_list' differs, since they
        contain the list of possible binwidths.

        If the constraints cannot be set in the fast counting hardware then
        write just zero to each key of the generic dicts.
        Note that there is a difference between float input (0.0) and
        integer input (0), because some logic modules might rely on that
        distinction.

        ALL THE PRESENT KEYS OF THE CONSTRAINTS DICT MUST BE ASSIGNED!
        """

        constraints = dict()

        # the unit of those entries are seconds per bin. In order to get the
        # current binwidth in seonds use the get_binwidth method.
        constraints['hardware_binwidth_list'] = [1/950e6, 2/950e6, 4/950e6, 8/950e6]

        return constraints

    def configure(self, bin_width_s, record_length_s, number_of_gates = 0):
        """
Configuration of the fast counter.

Parameters
----------
bin_width_s : float
    Length of a single time bin in the time trace histogram in seconds.
record_length_s : float
    Total length of the timetrace/each single gate in seconds.
number_of_gates : int, optional
    Number of gates in the pulse sequence. Ignore for non-gated counter.

Returns
-------
tuple
    A tuple containing:
    - binwidth_s : float
        The actual set binwidth in seconds.
    - gate_length_s : float
        The actual set gate length in seconds.
    - number_of_gates : int
        The number of gates that are accepted.
"""

        self._binwidth = int(np.rint(bin_width_s * 1e9 * 950 / 1000))
        self._gate_length_bins = int(np.rint(record_length_s / bin_width_s))
        actual_binwidth = self._binwidth * 1000 / 950e9
        actual_length = self._gate_length_bins * actual_binwidth
        self.statusvar = 1
        return actual_binwidth, actual_length, number_of_gates


    def get_status(self):
        """ Receives the current status of the Fast Counter and outputs it as
            return value.

        0 = unconfigured
        1 = idle
        2 = running
        3 = paused
        -1 = error state
        """
        return self.statusvar

    def start_measure(self):
        time.sleep(1)
        self.statusvar = 2
        try:
            self._count_data = np.loadtxt(self.trace_path, dtype='int64')
        except:
            return -1

        if self._gated:
            self._count_data = self._count_data.transpose()
        return 0

    def pause_measure(self):
        """ Pauses the current measurement.

        Fast counter must be initially in the run state to make it pause.
        """
        time.sleep(1)
        self.statusvar = 3
        return 0

    def stop_measure(self):
        """ Stop the fast counter. """

        time.sleep(1)
        self.statusvar = 1
        return 0

    def continue_measure(self):
        """ Continues the current measurement.

        If fast counter is in pause state, then fast counter will be continued.
        """

        self.statusvar = 2
        return 0

    def is_gated(self):
        """ Check the gated counting possibility.

        @return bool: Boolean value indicates if the fast counter is a gated
                      counter (TRUE) or not (FALSE).
        """

        return self._gated

    def get_binwidth(self):
        """ Returns the width of a single timebin in the timetrace in seconds.

        @return float: current length of a single bin in seconds (seconds/bin)
        """
        width_in_seconds = self._binwidth * 1/950e6
        return width_in_seconds

    def get_data_trace(self):
        """ Polls the current timetrace data from the fast counter.

        Return value is a numpy array (dtype = int64).
        The binning, specified by calling configure() in forehand, must be
        taken care of in this hardware class. A possible overflow of the
        histogram bins must be caught here and taken care of.
        If the counter is NOT GATED it will return a tuple (1D-numpy-array, info_dict) with
            returnarray[timebin_index]
        If the counter is GATED it will return a tuple (2D-numpy-array, info_dict) with
            returnarray[gate_index, timebin_index]

        info_dict is a dictionary with keys :
            - 'elapsed_sweeps' : the elapsed number of sweeps
            - 'elapsed_time' : the elapsed time in seconds

        If the hardware does not support these features, the values should be None
        """

        # include an artificial waiting time
        time.sleep(0.5)
        info_dict = {'elapsed_sweeps': None, 'elapsed_time': None}
        return self._count_data, info_dict

    def get_frequency(self):
        freq = 950.
        time.sleep(0.5)
        return freq
