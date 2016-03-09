# -*- coding: utf-8 -*-

"""
This file contains the QuDi hardware file to control Gigatronics Device.

QuDi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

QuDi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with QuDi. If not, see <http://www.gnu.org/licenses/>.

Copyright (C) 2015 Thomas Unden thomas.unden@uni-ulm.de
"""

import visa

from core.base import Base
from interface.microwave_interface import MicrowaveInterface


class MicrowaveGigatronics(Base, MicrowaveInterface):
    """ This is the Interface class to define the controls for the simple
        microwave hardware.
    """
    _modclass = 'MicrowaveInterface'
    _modtype = 'hardware'

    ## declare connectors
    _out = {'mwsourcegigatronics': 'MicrowaveInterface'}

    def __init__(self, manager, name, config = {}, **kwargs):
        c_dict = {'onactivate': self.activation,
                  'ondeactivate': self.deactivation}
        Base.__init__(self, manager, name, config, c_dict)

    def activation(self, e):
        """ Initialisation performed during activation of the module.

        @param object e: Event class object from Fysom.
                         An object created by the state machine module Fysom,
                         which is connected to a specific event (have a look in
                         the Base Class). This object contains the passed event,
                         the state before the event happened and the destination
                         of the state which should be reached after the event
                         had happened.
        """

        # checking for the right configuration
        config = self.getConfiguration()
        if 'gpib_address' in config.keys():
            self._gpib_address = config['gpib_address']
        else:
            self.logMsg('This is MWgigatronics: did not find >>gpib_address<< '
                        'in configration.', msgType='error')

        if 'gpib_timeout' in config.keys():
            self._gpib_timeout = int(config['gpib_timeout'])
        else:
            self._gpib_timeout = 10
            self.logMsg('This is MWgigatronics: did not find >>gpib_timeout<< '
                        'in configration. I will set it to 10 seconds.',
                        msgType='error')

        # trying to load the visa connection to the module
        self.rm = visa.ResourceManager()
        try:
            self._gpib_connection = self.rm.open_resource(self._gpib_address,
                                                          timeout=self._gpib_timeout)
        except:
            self.logMsg('This is MWgigatronics: could not connect to the GPIB '
                        'address >>{}<<.'.format(self._gpib_address),
                        msgType='error')
            raise

        self.logMsg('MWgigatronics initialised and connected to hardware.',
                    msgType='status')

    def deactivation(self, e):
        """ Deinitialisation performed during deactivation of the module.

        @param object e: Event class object from Fysom. A more detailed
                         explanation can be found in method activation.
        """
        self._gpib_connection.close()
        self.rm.close()

    def on(self):
        """ Switches on any preconfigured microwave output.

        @return int: error code (0:OK, -1:error)
        """

        self._gpib_connection.write(':OUTP ON')
        return 0


    def off(self):
        """ Switches off any microwave output.

        @return int: error code (0:OK, -1:error)
        """

        self._gpib_connection.write(':OUTP OFF')
        self._gpib_connection.write(':MODE CW')
        return 0


    def get_power(self):
        """ Gets the microwave output power.

        @return float: the power set at the device in dBm
        """
        return float(self._gpib_connection.ask(':POW?'))


    def set_power(self, power=None):
        """ Sets the microwave output power.

        @param float power: the power (in dBm) set for this device

        @return int: error code (0:OK, -1:error)
        """
        if power != None:
            self._gpib_connection.write(':POW {:f} DBM'.format(power))
            return 0
        else:
            return -1


    def get_frequency(self):
        """ Gets the frequency of the microwave output.

        @return float: frequency (in Hz), which is currently set for this device
        """

        return float(self._gpib_connection.ask(':FREQ?'))


    def set_frequency(self, freq=0.):
        """ Sets the frequency of the microwave output.

        @param float freq: the frequency (in Hz) set for this device

        @return int: error code (0:OK, -1:error)
        """
        if freq != None:
            self._gpib_connection.write(':FREQ {:e}'.format(freq))
            return 0
        else:
            return -1


    def set_cw(self, freq=None, power=None, useinterleave=None):
        """ Sets the MW mode to cw and additionally frequency and power

        @param float freq: frequency to set in Hz
        @param float power: power to set in dBm
        @param bool useinterleave: If this mode exists you can choose it.

        @return int: error code (0:OK, -1:error)

        Interleave option is used for arbitrary waveform generator devices.
        """
        error = 0
        self._gpib_connection.write(':MODE CW')

        if freq != None:
            error = self.set_frequency(freq)
        else:
            return -1
        if power != None:
            error = self.set_power(power)
        else:
            return -1

        return error

    def set_list(self, freq=None, power=None):
        """ Sets the MW mode to list mode

        @param list freq: list of frequencies in Hz
        @param float power: MW power of the frequency list in dBm

        @return int: error code (0:OK, -1:error)
        """
        error = 0

        if self.set_cw(freq[0],power) != 0:
            error = -1

        self._gpib_connection.write(':MODE LIST')
        self._gpib_connection.write(':LIST:SEQ:AUTO ON')
        self._gpib_connection.write(':LIST:DEL:LIST 1')
        FreqString = ' '
        for f in freq[:-1]:
            FreqString += '{:f},'.format(f)
        FreqString += '{:f}'.freq(-1)
        self._gpib_connection.write(':LIST:FREQ' + FreqString)
        self._gpib_connection.write(':LIST:POW'  + (' {:f},'.format(power * len(freq[:-1]))))
        self._gpib_connection.write(':LIST:DWEL' + (' {:f},'.format(0.3 * len(freq[:-1]))))
        # ask crashes on Gigatronics, so we have to omit the sanity check
        self._gpib_connection.write(':LIST:PREC 1')
        self._gpib_connection.write(':LIST:REP STEP')
        self._gpib_connection.write(':TRIG:SOUR EXT')
        self._gpib_connection.write(':OUTP ON')

        N = int(numpy.round(float(self._gpib_connection.ask(':LIST:FREQ:POIN?'))))
        if N != len(freq):
            error = -1

        return error

    def reset_listpos(self):#
        """ Reset of MW List Mode position to start from first given frequency

        @return int: error code (0:OK, -1:error)
        """

        self._gpib_connection.write(':MODE CW')
        self._gpib_connection.write(':MODE LIST')
        return 0

    def list_on(self):
        """ Switches on the list mode.

        @return int: error code (0:OK, -1:error)
        """

        self._gpib_connection.write(':LIST:PREC 1')
        self._gpib_connection.write(':LIST:REP STEP')
        self._gpib_connection.write(':TRIG:SOUR EXT')
        self._gpib_connection.write(':MODE LIST')
        self._gpib_connection.write(':OUTP ON')

        return 0

    def set_ex_trigger(self, source, pol):
        """ Set the external trigger for this device with proper polarization.

        @param str source: channel name, where external trigger is expected.
        @param str pol: polarisation of the trigger (basically rising edge or
                        falling edge)

        @return int: error code (0:OK, -1:error)
        """
        return 0




