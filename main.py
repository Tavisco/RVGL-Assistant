# -*- coding: utf-8 -*-

import os
import yaml
import subprocess
import faulthandler
import io
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from gui import Ui_MainWindow
from menu_bar import *
from config import Config

faulthandler.enable()
configs = Config()
configs_loaded = False


class RVGLAssistantProgram(Ui_MainWindow):
    def __init__(self, window):
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # Handles the menubar items
        self.actionExit.triggered.connect(menu_action_exit)
        self.actionChange_RVGL_Path.triggered.connect(choose_custom_rvgl_location)

        # Handles the launch button
        self.btn_launch.clicked.connect(execute_rvgl)

        # Handles the Parameters


def execute_rvgl():
    if configs.rvgl_found:
        print('Launching RVGL')
        os.chdir(configs.rvgl_custom_path)
        path = os.path.join(configs.rvgl_custom_path, configs.rvgl_executable)
        subprocess.Popen([path])
        exit(0)
    else:
        look_for_rvgl()


def look_for_rvgl():
    global configs_loaded
    if configs_loaded:
        return

    configs.rvgl_found = choose_rvgl_executable()

    if not configs.rvgl_found:
        # noinspection PyTypeChecker
        QtWidgets.QMessageBox.warning(None, 'RVGL not found!',
                                      "RVGL wasn't found automatically!\nOn the next dialog, please select the game "
                                      "path")
        choose_custom_rvgl_location()


def choose_rvgl_executable(path='.'):
    rvgl_possible_executables = ['rvgl.64', 'rvgl.32', 'rvgl.exe']

    # First we look for any RVGL executable on the Assistant's path
    files = [f for f in os.listdir(path)]
    for f in files:
        if rvgl_possible_executables.__contains__(f):
            configs.rvgl_executable = f
            print("Setting RVGL executable to " + f)
            configs.rvgl_found = True
            save_configs()
            return True

    return False


def choose_custom_rvgl_location():
    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Choose RVGL path", "",
                                                          "All Files (*.*);", options=options)

    if path:
        configs.rvgl_custom_path = path
        print("Setting RVGL path to " + configs.rvgl_custom_path)
        choose_rvgl_executable(path=configs.rvgl_custom_path)


def save_configs():
    with io.open('./assistant.yml', 'w', encoding='utf8') as outfile:
        yaml.dump(configs, outfile, default_flow_style=False, allow_unicode=True)
        print('Configs saved')


def load_configs():
    global configs, configs_loaded
    # We first check if the config file exists
    config_file = Path("./assistant.yml")
    if config_file.is_file():
        with open("./assistant.yml", 'r') as ymlfile:
            configs = yaml.load(ymlfile)
            configs_loaded = True
            print('Configs loaded!')
            #yaml.dump(configs, sys.stdout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    prog = RVGLAssistantProgram(MainWindow)

    load_configs()
    look_for_rvgl()

    MainWindow.show()
    sys.exit(app.exec_())
