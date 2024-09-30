# -*- coding: utf-8 -*-
"""
This module controls LaserQuantum lasers.

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

try:
    import pyvisa as visa
except ImportError:
    import visa
from qudi.core.configoption import ConfigOption
from qudi.interface.simple_laser_interface import SimpleLaserInterface
from qudi.interface.simple_laser_interface import ControlMode, ShutterState, LaserState


class MillenniaeVLaser(SimpleLaserInterface):
    """ Spectra Physics Millennia diode pumped solid state laser.

    Example config for copy-paste:

    millennia_laser:
        module.Class: 'laser.millennia_ev_laser.MillenniaeVLaser'
        options:
            interface: 'ASRL1::INSTR'
            maxpower: 25 # in Watt

    """

    serial_interface = ConfigOption(name='interface', default='ASRL1::INSTR', missing='warn')
    maxpower = ConfigOption(name='maxpower', default=25.0, missing='warn')

    def on_activate(self):
        """ Activate Module.
        """
        self._control_mode = ControlMode.POWER
        self.connect_laser(self.serial_interface)

    def on_deactivate(self):
        """ Deactivate module
        """
        self.disconnect_laser()

    def connect_laser(self, interface):
        """
Connect to the instrument.

Parameters
----------
str interface
    Visa interface identifier.

Returns
-------
bool
    Connection success.
"""

        try:
            self.rm = visa.ResourceManager()
            rate = 115200
            self.inst = self.rm.open_resource(
                interface,
                baud_rate=rate,
                write_termination='\n',
                read_termination='\n',
                send_end=True)
            self.inst.timeout = 1000
            idn = self.inst.query('*IDN?')
            (self.mfg, self.model, self.serial, self.version) = idn.split(',')
        except visa.VisaIOError as e:
            self.log.exception('Communication Failure:')
            return False
        else:
            return True

    def disconnect_laser(self):
        """ Close the connection to the instrument.
        """
        self.inst.close()
        self.rm.close()

    def allowed_control_modes(self):
        """
Control modes for this laser.

Returns
-------
ControlMode
    Available control modes.
"""

        return {ControlMode.POWER, ControlMode.CURRENT}

    def get_control_mode(self):
        """
Get active control mode.

Returns
-------
ControlMode
    Active control mode.
"""

        return self._control_mode

    def set_control_mode(self, mode):
        """
Set active control mode.

Parameters
----------
mode : ControlMode
    Desired control mode.

Returns
-------
ControlMode
    Actual control mode.
"""

        if mode in self.allowed_control_modes():
            self._control_mode = mode

    def get_power(self):
        """
Current laser power.

Returns
-------
float
    Laser power in watts.
"""

        return float(self.inst.query('?P'))

    def get_power_setpoint(self):
        """
Current laser power setpoint.

Returns
-------
float
    Power setpoint in watts.
"""

        return float(self.inst.query('?PSET'))

    def get_power_range(self):
        """
Laser power range.

Returns
-------
float[2]
    Laser power range.
"""

        return 0, self.maxpower

    def set_power(self, power):
        """
Set laser power setpoint.

Parameters
----------
power : float
    Desired laser power in watts.
"""

        self.inst.query('P:{0:f}'.format(power))

    def get_current_unit(self):
        """
Get unit for current.

Returns
-------
str
    Unit for laser current.
"""

        return 'A'

    def get_current_range(self):
        """
Get range for laser current.

Returns
-------
float[2]
    Range for laser current.
"""

        return 0, float(self.inst.query('?DCL'))

    def get_current(self):
        """
Get current laser current.

Returns
-------
float
    Current laser current.
"""

        return float(self.inst.query('?C1'))

    def get_current_setpoint(self):
        """
Get laser current setpoint.

Returns
-------
float
    Laser current setpoint.
"""

        return float(self.inst.query('?CS1'))

    def set_current(self, current_percent):
        """
Set laser current setpoint.

Parameters
----------
current_percent : float
    Desired laser current setpoint.

Returns
-------
float
    Actual laser current setpoint.
"""

        self.inst.query('C:{0}'.format(current_percent))

    def get_shutter_state(self):
        """
Get laser shutter state.

Returns
-------
ShutterState
    Current laser shutter state.
"""

        state = self.inst.query('?SHT')
        if 'OPEN' in state:
            return ShutterState.OPEN
        elif 'CLOSED' in state:
            return ShutterState.CLOSED
        else:
            return ShutterState.UNKNOWN

    def set_shutter_state(self, state):
        """
Set laser shutter state.

Parameters
----------
ShutterState state : desired laser shutter state

Returns
-------
ShutterState
    Actual laser shutter state.
"""

        if state != self.get_shutter_state():
            if state == ShutterState.OPEN:
                self.inst.query('SHT:1')
            elif state == ShutterState.CLOSED:
                self.inst.query('SHT:0')

    def get_crystal_temperature(self):
        """
Get SHG crystal temperature.

Returns
-------
float
    SHG crystal temperature in degrees Celsius.
"""

        return float(self.inst.query('?SHG'))

    def get_diode_temperature(self):
        """
Get laser diode temperature.

Returns
-------
float
    Laser diode temperature in degrees Celsius.
"""

        return float(self.inst.query('?T'))

    def get_tower_temperature(self):
        """
Get SHG tower temperature.

Returns
-------
float
    SHG tower temperature in degrees Celsius.
"""

        return float(self.inst.query('?TT'))

    def get_cab_temperature(self):
        """
Get cabinet temperature.

Returns
-------
float
    Laser cabinet temperature in degrees Celsius.
"""

        return float(self.inst.query('?CABTEMP'))

    def get_temperatures(self):
        """
Get all available temperatures.

Returns
-------
dict
    A dictionary where keys are temperature names and values are their corresponding temperature readings.
"""

        return {
            'crystal': self.get_crystal_temperature(),
            'diode': self.get_diode_temperature(),
            'tower': self.get_tower_temperature(),
            'cab': self.get_cab_temperature()
        }

    def get_laser_state(self):
        """
Get the current laser state.

Returns
-------
LaserState
    The current state of the laser.
"""

        diode = int(self.inst.query('?D'))
        state = self.inst.query('?F')

        if state in ('SYS ILK', 'KEY ILK'):
            return LaserState.LOCKED
        elif state == 'SYSTEM OK':
            if diode == 1:
                return LaserState.ON
            elif diode == 0:
                return LaserState.OFF
            else:
                return LaserState.UNKNOWN
        else:
            return LaserState.UNKNOWN

    def set_laser_state(self, status):
        """
Set the desired laser state.

Parameters
----------
status : LaserState
    The desired laser state to set.

Returns
-------
LaserState
    The actual laser state after the operation.
"""

        if self.get_laser_state() != status:
            if status == LaserState.ON:
                self.inst.query('ON')
            elif status == LaserState.OFF:
                self.inst.query('OFF')

    def dump(self):
        """
Dump laser information.

Returns
-------
str
    A string containing the laser information.
"""

        return 'Didoe Serial: {0}\n'.format(self.inst.query('?DSN'))

    def timers(self):
        """
Laser component runtimes.

Returns
-------
str
    A string containing the laser component run times.
"""

        lines = 'Diode ON: {0}\n'.format(self.inst.query('?DH'))
        lines += 'Head ON: {0}\n'.format(self.inst.query('?HEADHRS'))
        lines += 'PSU ON: {0}\n'.format(self.inst.query('?PSHRS'))
        return lines

    def get_extra_info(self):
        """
Formatted information about the laser.

Returns
-------
str
    Laser information.
"""

        extra = '{0}\n{1}\n{2}\n{3}\n'.format(self.mfg, self.model, self.serial, self.version)
        extra += '\n'
        extra += '\n {0}'.format(self.timers())
        extra += '\n'
        return extra
