import pytest
from qudi.core import application,modulemanager
from qudi.util.yaml import yaml_load
from PySide2 import QtWidgets
import weakref
import logging
import sys 
import os


CONFIG = os.path.join(os.getcwd(),'tests/test.cfg')

@pytest.fixture(scope="module")
def qt_app():
    app_cls = QtWidgets.QApplication
    app = app_cls.instance()
    if app is None:
        app = app_cls()
    return app

@pytest.fixture(scope="module")
def qudi_instance():
    instance = application.Qudi.instance()
    if instance is None:
        instance = application.Qudi(config_file=CONFIG)
    instance_weak = weakref.ref(instance)
    return instance_weak()

@pytest.fixture(scope="module")
def module_manager(qudi_instance):
    return qudi_instance.module_manager

@pytest.fixture(scope='module')
def config():
    configuration = (yaml_load(CONFIG))
    return configuration



