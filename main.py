# -*- coding: utf-8 -*-

import os
import yaml
import subprocess
import faulthandler; faulthandler.enable()
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog
from threading import Thread
from gui import Ui_MainWindow
from menu_bar import *

rvgl_found = False
rvgl_custom_path = ""
rvgl_executable = ""
configs = ""


class RVGLAssistantProgram(Ui_MainWindow):
    def __init__(self, window):
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # Handles the menubar items
        self.actionExit.triggered.connect(menu_action_exit)
        self.actionChange_RVGL_Path.triggered.connect(choose_custom_rvgl_location)

        # Handles the launch button
        self.btn_launch.clicked.connect(launch_rvgl)

        # Handles the Parameters


def launch_rvgl():
    thread = Thread(target=execute_rvgl())
    thread.start()
    thread.join()


def execute_rvgl():
    print('Launching RVGL')
    os.chdir(rvgl_custom_path)
    path = os.path.join(rvgl_custom_path, rvgl_executable)
    print(path)
    subprocess.Popen(executable=path, args="")
    # exit(0)


def look_for_rvgl():
    global rvgl_found

    rvgl_found = choose_rvgl_executable()

    if not rvgl_found:
        # noinspection PyTypeChecker
        QtWidgets.QMessageBox.warning(None, 'RVGL not found!',
                                      "RVGL wasn't found automatically!\nOn the next dialog, please select the game "
                                      "path")
        choose_custom_rvgl_location()


def choose_rvgl_executable(path='.'):
    global rvgl_executable
    rvgl_possible_executables = ['rvgl.64', 'rvgl.32', 'rvgl.exe']

    # First we look for any RVGL executable on the Assistant's path
    files = [f for f in os.listdir(path)]
    for f in files:
        if rvgl_possible_executables.__contains__(f):
            rvgl_executable = f
            print("Setting RVGL executable to " + f)
            return True

    return False


def choose_custom_rvgl_location():
    global rvgl_found, rvgl_custom_path

    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Choose RVGL path", "",
                                                          "All Files (*.*);", options=options)

    if path:
        rvgl_found = True
        rvgl_custom_path = path
        print("Setting RVGL path to " + rvgl_custom_path)
        choose_rvgl_executable(path=rvgl_custom_path)


def load_configs():
    global configs
    # We first check if the config file exists
    config_file = Path("./assistant.yml")
    if config_file.is_file():
        with open("./assistant.yml", 'r') as ymlfile:
            configs = yaml.load(ymlfile)
            yaml.dump(configs, sys.stdout)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    prog = RVGLAssistantProgram(MainWindow)

    # load_configs()
    look_for_rvgl()

    MainWindow.show()
    sys.exit(app.exec_())
