# -*- coding: utf-8 -*-

"""
This file contains unit tests for all qudi fit routines for exponential decay models.

Copyright (c) 2021, the qudi developers. See the AUTHORS.md file at the top-level directory of this
distribution and on <https://github.com/Ulm-IQO/qudi-core/>

This file is part of qudi.

Qudi is free software: you can redistribute it and/or modify it under the terms of
the GNU Lesser General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

Qudi is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License along with qudi.
If not, see <https://www.gnu.org/licenses/>.
"""

import pytest
import rpyc
import multiprocessing
from qudi.core import application
from PySide2 import QtWidgets
from PySide2.QtCore import QTimer
import os
import time

CONFIG = os.path.join(os.getcwd(),'tests/test.cfg')

def run_qudi():
    app_cls = QtWidgets.QApplication
    app = app_cls.instance()
    if app is None:
        app = app_cls()
    qudi_instance = application.Qudi.instance()
    if qudi_instance is None:
        qudi_instance = application.Qudi(config_file=CONFIG)
    QTimer.singleShot(150000, qudi_instance.quit)
    qudi_instance.run()


@pytest.fixture(scope='module', autouse=True)
def start_qudi_process():
    """This fixture starts the Qudi process and ensures it's running before tests."""
    qudi_process = multiprocessing.Process(target=run_qudi)
    qudi_process.start()
    time.sleep(10)
    yield
    qudi_process.join(timeout=10)
    if qudi_process.is_alive():
        qudi_process.terminate()

@pytest.fixture(scope='module')
def remote_instance():
    time.sleep(10)
    conn = rpyc.connect("localhost", 18861, config={'sync_request_timeout': 60})
    root = conn.root

    qudi_instance = root._qudi
    return qudi_instance


'''
#This test fails for some modules such as ODMR  PulsedGUI
def test_reset_module(gui_modules, hardware_modules, remote_instance):
    """This tests clearing all the logic module status variables and reloads the GUI modules

    Parameters
    ----------
    gui_modules : Fixture
        List of gui module names
    hardware_modules : Fixture
        List of hardware module names
    remote_instance : Fixture
        Remote qudi rpyc instance
    """    
    module_manager = remote_instance.module_manager
    modules = module_manager.modules
    for module in modules:
        module_manager.deactivate_module(module)

        module_manager.clear_module_app_data(module)
        module_manager.reload_module(module)

    for gui_module in gui_modules:
        gui_managed_module = module_manager.modules[gui_module]
        required_managed_modules = gui_managed_module.required_modules
        required_modules = [required_managed_module().name for required_managed_module in required_managed_modules]

        linked_required_managed_modules = [required_managed_module().required_modules for required_managed_module in required_managed_modules]      
        linked_required_modules = []
        for linked_required_managed_module in linked_required_managed_modules:
            linked_required_modules.extend([required_managed_module().name for required_managed_module in linked_required_managed_module])

        required_logic_modules = required_modules
        required_logic_modules.extend([linked_required_module for linked_required_module in linked_required_modules if linked_required_module not in hardware_modules ])
        #print(f'for {gui_module}, required logic are {required_logic_modules}')
        module_manager.activate_module(gui_module)

        for required_logic_module in required_logic_modules:
            module_manager.deactivate_module(required_logic_module)
            module_manager.clear_module_app_data(required_logic_module)
            #module_manager.reload_module(required_logic_module)
            #module_manager.activate_module(required_logic_module)
        
        module_manager.activate_module(gui_module)
        gui_managed_module = module_manager.modules[gui_module]
        assert gui_managed_module.is_active

        time.sleep(10)
        module_manager.deactivate_module(gui_module)


'''
