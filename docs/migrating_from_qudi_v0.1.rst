.. _migrating_from_qudi:

Migrating from old Qudi (release v0.1) to New Core
==================================================

This document provides a short overview of how to migrate from an existing
Qudi installation (<= v0.1) to the new Qudi release vXXX (aka new core).
You can easily keep your old installation in parallel. Moving to the
new core is mainly about porting your old configuration file. The good
news is: If you have a running configuration for v0.1 already, it should
be straightforward to adapt it to your new Qudi installation. Please
note that we are describing the most common use case, but cannot cover
all modules here. If you encounter issues with any configuration, it
might help to look into the source (.py) file. There, you'll find an
example config in the docstring of the respective class.

General Qudi Config
-------------------

The core Qudi facilities are configured in the ‘global’ section of the
config file. You can find a detailed description in the Qudi-core
:ref:`configuration guide <core:configuration>`.
It might be helpful to have a look at the respective section in the
`default config <https://github.com/Ulm-IQO/qudi-iqo-modules/blob/main/src/qudi/default.cfg>`__
which sets up a dummy configuration without real hardware.

Remote Modules
~~~~~~~~~~~~~~

The setup of remote connections has changed quite a bit. Please refer to the
instructions to configure the 
:ref:`server <core:remote_modules_server>`
and each of the 
:ref:`remote modules <core:configuration:remote_module>.

Qudi Kernel
~~~~~~~~~~~

When switching between an old (v0.1) installation and the new core, you need to 
register the Qudi kernel.

- Open your Anaconda prompt and activate the respective Qudi environment:

Before starting the new core:

::

   activate qudi-env
   qudi-install-kernel

Before starting your old installation:

::

   activate qudi 
   cd C:\Software\qudi\core
   python qudikernel.py install

Module Config
-------------

The configuration for the following modules has changed substantially:

- :ref:`timeseries <time_series>`

   ::

      Formerly known as slow counter. The new implementation is more flexible 
      and allows more data sources (than the TTL counting supported by our old 
      slow counter).

- :ref:`scanning <scanning>`

   Formerly known as confocal. The refined version was rewritten from 
   scratch and supports arbitrary input sources and axis configurations.

- :ref:`cw odmr <odmr>`

   The toolchain has changed, but this doesn’t affect the configuration much. 
   Changes in the cw odmr configuration result from major restructuring of the NI card 
   duties. For cw odmr, ``ni_x_finite_sampling_input`` is required. For the correct 
   configuration, please refer to the example config in the docstring of the 
   ``NIXSeriesFiniteSamplingInput`` class in 
   ``qudi\hardware\ni_x_series\ni_x_series_finite_sampling_input.py``.
   
   All ports need to be adapted to your custom setup, of course. You should
   find the correct ports in your old configuration of the NI card.

For the following modules, no or only minimal changes should be required:
- laser
- pulsed

Known Missing Features
======================

Compared to the old release v0.1, the following features are currently
not available yet:

- Magnet control GUI
- Confocal/Scanning: tilt correction, loop scans, moving arbitrary axis during scan, pause and resume scan
- Wavemeter toolchain
- Hardware PID (Software PID is coming soon, currently in testing PR)

If you need these features, please reach out to us to discuss how
to move forward. We might have already started to port a feature or can
assist you in contributing.

Untested Features
=================

Some of the toolchains and modules have been ported but not thoroughly
tested yet. Please let us know if you successfully use or find errors in
the following modules:

- motors hardware files
- power supply hardware files
- temperature
- camera toolchain

Miscellaneous
=============
