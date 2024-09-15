.. _odmr:

Odmr
====

A typical working toolchain consists of the following Qudi modules:

- **logic**: 
  - `odmr_logic`
  
- **hardware**:
  - `microwave`, e.g., `mw_source_smiq`
  - `data_scanner`, e.g., `ni_finite_sampling_input`

- **gui**:
  - `odmrgui`

Example Config
==============

These modules need to be configured and connected in your Qudi config
file. Below is an example config for a toolchain based on a NI
X-series scanner with analogue output and digital (APD TTL) input.

.. note::
   This readme might not be up-to-date with the most recent development. 
   We recommend checking the example config present in the docstring of 
   every module’s Python file. In the list above, a direct link for 
   every module is provided:

.. code-block:: yaml

   gui:
       odmr_gui:
           module.Class: 'odmr.odmrgui.OdmrGui'
           connect:
               odmr_logic: 'odmr_logic'

   logic:
       odmr_logic:
           module.Class: 'odmr_logic.OdmrLogic'
           connect:
               microwave: mw_source_smiq
               data_scanner: ni_finite_sampling_input

   hardware:
       mw_source_smiq:
           module.Class: 'microwave.mw_source_smiq.MicrowaveSmiq'
           options:
               visa_address: 'GPIB0::28::INSTR'
               comm_timeout: 10000  # in milliseconds
               visa_baud_rate: null  # optional
               rising_edge_trigger: True  # optional
               frequency_min: null  # optional, in Hz
               frequency_max: null  # optional, in Hz
               power_min: null  # optional, in dBm
               power_max: null  # optional, in dBm

       ni_finite_sampling_input:
           module.Class: 'ni_x_series.ni_x_series_finite_sampling_input.NIXSeriesFiniteSamplingInput'
           options:
               device_name: 'Dev1'
               digital_channel_units:  # optional
                   'PFI15': 'c/s'
               analog_channel_units:  # optional
                   'ai0': 'V'
                   'ai1': 'V'
               # external_sample_clock_source: 'PFI0'  # optional
               # external_sample_clock_frequency: 1000  # optional
               adc_voltage_range: [-10, 10]  # optional, default [-10, 10]
               max_channel_samples_buffer: 10000000  # optional, default 10000000
               read_write_timeout: 10  # optional, default 10
               sample_clock_output: '/Dev1/PFI20'  # optional
       

Configuration Hints
===================

Make sure that the hardware in the config file is named as it is referred to
by the logic (copy-pasting from the hardware file can result in 
differently named entries).

Todo This Readme
================

