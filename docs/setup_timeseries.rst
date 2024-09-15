.. _time_series:

Time Series
===========

The timeseries toolchain allows plotting the timetrace of an incoming
digital or analogue signal in real time. For a confocal setup, the
signal might be TTLs coming from a photon counter or the (analogue)
output of a photodiode. A typical working toolchain consists of the
following Qudi modules:

- **logic**:
  - `time_series_reader_logic`

- **hardware**:
  - `instreamer`, e.g., `ni_instreamer`

- **gui**:
  - `time_series_gui`

Example Config
==============

These modules need to be configured and connected in your Qudi config
file. Below is an example config for a toolchain based on a NI
X-series scanner with analogue output and digital (APD TTL) input.

.. note::
   This readme might not be up-to-date with the most recent
   development. We recommend checking the example config present in the
   docstring of every module’s Python file. In the list above, a direct
   link for each module is provided:

.. code-block:: yaml

   gui:
     time_series_gui:
         module.Class: 'time_series.time_series_gui.TimeSeriesGui'
         options:
           use_antialias: True  # optional, set to False if you encounter performance issues
         connect:
             _time_series_logic_con: time_series_reader_logic

   logic:
     time_series_reader_logic:
       module.Class: 'time_series_reader_logic.TimeSeriesReaderLogic'
       options:
           max_frame_rate: 20  # optional (10Hz by default)
           calc_digital_freq: True  # optional (True by default)
       connect:
           streamer: ni_instreamer

   hardware:
       ni_instreamer:
         module.Class: 'ni_x_series.ni_x_series_in_streamer.NIXSeriesInStreamer'
         options:
             device_name: 'Dev1'
             digital_sources:  # optional
                 - 'PFI8'
             #analog_sources:  # optional
                 #- 'ai0'
                 #- 'ai1'
             # external_sample_clock_source: 'PFI0'  # optional
             # external_sample_clock_frequency: 1000  # optional
             adc_voltage_range: [-10, 10]  # optional
             max_channel_samples_buffer: 10000000  # optional
             read_write_timeout: 10  # optional

Configuration Hints
===================

Make sure that the hardware in the config file is named as it is referred to
by the logic (copy-pasting from the hardware file can result in
differently named entries).

Todo This Readme
================
