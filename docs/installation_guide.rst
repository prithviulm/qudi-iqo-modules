Installation Guide
==================

This guide provides step-by-step instructions on how to get started with the **qudi** + **iqo-modules** installation. For additional information, refer to the :ref:`qudi-core documentation <core:installation>`. If you’re migrating an existing qudi v0.1 installation, consult the :ref:`porting guide <_migrating_from_qudi>`.

Install qudi core
-----------------

Follow the :ref:`qudi-core installation <core:installation>` instructions to set up your Python environment and the basic qudi installation. We recommend installing **qudi-core** from PyPI (non-dev) as typical users don’t need to change core code frequently. However, you can still modify measurement modules, which are installed next.

Installing Qudi-IQO Modules
---------------------------

The last step in the qudi-core installation instructions briefly explains setting up the measurement modules. Below are the detailed steps to install the qudi-iqo-modules in development mode, allowing you to easily modify the code in the measurement toolchains.

Steps:
~~~~~~

1. **Ensure Git is Installed**

   Make sure you have a working Git installation, and you can run the ``git`` command from your console.

2. **Activate Your Environment**

   Open your Anaconda prompt and activate your Qudi environment by running:

   .. code-block:: console

      activate qudi-env

   Alternatively, if you're using a different Python distribution, activate the corresponding virtual environment.

3. **Navigate to Your Desired Installation Folder**

   Move to the folder where you want to install the modules. For example:

   .. code-block:: console

      cd C:/Software

4. **Clone the IQO Modules Repository**

   Clone the iqo-modules repository using Git by running:

   .. code-block:: console

      git clone https://github.com/Ulm-IQO/qudi-iqo-modules.git

   This will create a new folder: ``C:/Software/qudi-iqo-modules``.

   .. note:: Do not copy or move this folder after installation is complete!

5. **Navigate to the Qudi-IQO Modules Folder**

   Enter the newly created folder:

   .. code-block:: console

      cd C:/Software/qudi-iqo-modules

6. **Install and Register the Modules**

   To install and register the modules in your current Qudi environment, run:

   .. code-block:: console

      python -m pip install -e .

Once completed, your Qudi-core installation will recognize the measurement modules. At this point, it's time to set up a proper Qudi configuration file.


⚠ Troubleshooting
------------------

-  Installing according to this guide will leave you with the most
   recent version of qudi and all dependency packages. If you encounter
   bugs, especially ones that relate to dependency packages, you can
   roll back to the latest stable release by:

   ::

      cd C:/Software/qudi-iqo-modules
      git checkout tags/v0.5.1
      python -m pip install -e .

-  In rare cases, mostly with old versions of qudi-core, 
   qudi-iqo-modules can be incompatible with qudi-core. If you encounter 
   errors related to this, try to manually update to the latest 
   qudi-core GitHub release via:

   ``python -m pip install git+https://github.com/Ulm-IQO/qudi-core.git@main``


Configure PyCharm
-----------------

It is possible to run Qudi just from the command line. To do so, simply
type ``qudi`` into your console. However, having the code as a project in the 
PyCharm IDE allows for easier navigation and running of the qudi code.

-  Open your Anaconda prompt and ``activate qudi-env`` (or activate your
   venv in your other Python distribution).

-  Create a new empty project in PyCharm. Don’t open any source code yet.

To run Qudi via PyCharm, you have to configure the correct Python
environment as a project interpreter:

-  In PyCharm, navigate to ‘File’ -> ‘Settings’ -> ‘Project:qudi’ -> 
   ‘Project Interpreter’.

-  If the correct environment is not listed, you can add it via the "+" button. 
   If you followed the qudi-core installation instructions, the environment 
   should be named ``qudi-env`` (or whatever name you gave it during the core installation).

-  You can find the path to the environment by running the following command 
   (make sure to activate your qudi environment first!):

   .. code-block:: console

      python -c "import os, sys; print(os.path.dirname(sys.executable))"

-  Choose the correct environment, as shown in the screenshot.

Now we can open the code in PyCharm:

-  Add the `qudi-iqo-modules` (and potentially `qudi-core`) folder by 
   navigating to ‘File’ -> ‘Open..’. After selecting the folder, a pop-up window 
   will ask you how to open the project. Press the ‘Attach’ option to have 
   separate locations open in the same project.

-  If you installed qudi-core in non-developer mode, you can find your 
   qudi-core folder by running:

   .. code-block:: console

      python -c "import os, sys; print(os.path.dirname(sys.executable)+'\\Lib\\site-packages\\qudi')"

-  Now navigate in PyCharm to ‘Run’ -> ‘Edit Configuration’ and create a 
   new ‘Shell Script’ configuration, as shown below. The ‘-d’ flag enables debug output 
   and is optional.

You can now run Qudi from PyCharm via ‘Run’ -> ‘Run qudi’.

Switching Branches
~~~~~~~~~~~~~~~~~~

Switching to another development branch is easy if you installed your 
modules in dev mode. Simply look in the lower right corner of PyCharm to 
access the branch control, and ‘checkout’ the desired branch from 
`remote/origin` (i.e., branches available online, not local copies on your computer).

You will now have a local copy of this branch, in which you can create 
commits and push these online.


Qudi Configuration
------------------

The configuration file specifies all the modules and hardware that are
loaded into Qudi. Additionally, many modules come with configuration
parameters that are set in this file. On your first startup, the Qudi
manager might be empty. As a first step, it is helpful to load the 
default `dummy configuration <https://github.com/Ulm-IQO/qudi-iqo-modules/blob/main/src/qudi/default.cfg>`__
that we provide with qudi-iqo-modules. This allows you to explore the
available toolchains and modules without the need to attach real
hardware.

-  Copy the default.cfg (from 
   ``qudi-iqo-modules\src\qudi\default.cfg``) 
   into your user data folder, e.g., to 
   ``C:\Users\quantumguy\qudi\config``. 
   We strongly advise against storing any configuration (except the 
   default.cfg) in the source folder of Qudi.
   
-  Start Qudi, and then load (via `File -> Load configuration`) the 
   default config that you just copied.

-  Currently, we provide the following toolchains:

   - :ref:`Time series <time_series>`
     (*slow counting*)
   - :ref:`Scanning <scanning>`
     (*confocal*)
   - Poi manager
   - :ref:`CW ODMR <odmr>`
   - Pulsed
   - Camera
   - Switches
   - Laser
   - Spectrometer
   - Task runner
   - Qdplot
   - NV Calculator

-  Continue by setting up real hardware. For more complex toolchains, 
   links to help files have been provided to assist in their configuration.
   Otherwise, we recommend starting with the respective GUI section in 
   the dummy config file and iteratively working through all the 
   connected modules (logic/hardware) to adapt them for use with 
   real hardware.

As an IQO member, we strongly recommend storing your configuration in
the `qudi-iqo-config repo <https://github.com/Ulm-IQO/qudi-iqo-config>`__.
In this repository, you can find configurations for multiple setups at 
the institute.

-  To set this up, navigate in your console to the folder where you want 
   to store your configuration. We recommend your user directory, 
   because Qudi, by default, stores logs and data there:

   .. code-block:: console

      cd C:\Users\quantumguy\qudi

-  Clone the repository from git:

   .. code-block:: console

      git clone https://github.com/Ulm-IQO/qudi-iqo-config

-  Open the created folder in PyCharm via `File -> Open -> Attach`.
-  Copy your configuration file into this folder.
-  Commit your file by right-clicking on it in PyCharm -> `Git -> Commit`.
-  Push your changes online via `Git -> Push`.

Whenever you make changes to your configuration, you should commit it 
and make it available online. All configurations in this repo are visible
only to IQO members.

Remote
~~~~~~

Qudi allows access to modules (including hardware) that run on a
different computer connected to the same LAN network. Please refer to the
:ref:`configuration instructions <core:remote_modules>`
in the qudi-core documentation.

Jupyter Notebooks / Measurement Scripts
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Qudi runs an IPython kernel that can be accessed from a Jupyter notebook.
This allows you to write your own measurement scripts as described
:ref:`here <core:jupyter>`.

Comparing Notebooks
~~~~~~~~~~~~~~~~~~~

PyCharm allows you to easily compare text-based files (like .py) between
different branches or versions by right-clicking on the file and
choosing `Git -> Compare with`. This comparison method, however, does 
not work for content-enriched files like Jupyter notebooks (.ipynb).
For similar functionality, you can configure PyCharm to use the 
``nbdime`` tool.

-  Open your Anaconda prompt and `activate qudi-env` (or activate your 
   venv in your other Python distribution).
-  Install ``nbdime`` via:

   .. code-block:: console

      conda install nbdime

-  Find the executable of ``nbdime`` by running:

   .. code-block:: console

      where nbdiff-web

-  In PyCharm, navigate to `File -> Settings -> Tools -> Diff and Merge -> 
   External Diff Tools`, and paste the path to the executable in the 
   ‘Path to executable’ field.

-  Add the following as Parameters:

   .. code-block:: console

      --ignore-details --ignore-metadata --ignore-outputs %1 %2

Now you can open nbdime from PyCharm’s diff tool by hitting the hammer
symbol.

Transcribing Scripts from Qudi v0.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IPython in Qudi (either in the Manager or a Jupyter notebook) now runs
in its own process. Communication between Qudi and the corresponding 
IPython process is handled via `rpyc`.

Non-Python built-in objects need to be copied using `netobtain()`. We 
plan to provide in-depth documentation in the new core.
