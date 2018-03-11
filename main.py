# -*- coding: utf-8 -*-

import os
import yaml
import subprocess
import faulthandler
import io
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QMessageBox
from gui import Ui_MainWindow
from menu_bar import *

faulthandler.enable()
configs = {}
configs_loaded = False
selected_params = []
lst_profiles = ""


class RVGLAssistantProgram(Ui_MainWindow):
    def __init__(self, window):
        global lst_profiles, configs_loaded
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # Handles the menubar items
        self.actionExit.triggered.connect(menu_action_exit)
        self.actionChange_RVGL_Path.triggered.connect(choose_custom_rvgl_location)

        # Handles the buttons
        self.btn_launch.clicked.connect(execute_rvgl)
        self.btn_save.clicked.connect(save_profile)
        self.btn_delete.clicked.connect(delete_profile)

        # Handles the Parameters
        checkboxes = []
        for i_layout in range(6):
            layout = getattr(self, 'layout_params_{}'.format(i_layout + 1))
            for i in range(layout.count()):
                widget = layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QCheckBox):
                    checkboxes.append(widget)

        for checkbox in checkboxes:
            checkbox.clicked.connect(lambda _, chk=checkbox: handle_param_click(checkbox=chk))

        lst_profiles = self.lst_profiles

        if configs_loaded:
            # Populate the profiles list
            for profile in configs['profiles']:
                lst_profiles.addItem(profile)

            # Loads the default checkboxes from config
            if len(configs['profiles']) > 0:
                first_profile = list(configs['profiles'].keys())[0]
                print('Loading \'{}\' profile'.format(first_profile))
                for parameter in configs['profiles'][first_profile]:
                    clean_parameter = parameter.replace('-', '')
                    checkbox = getattr(self, 'chk_param_{}'.format(clean_parameter))
                    checkbox.click()


def handle_param_click(checkbox):
    global selected_params
    param = checkbox.text().replace('&', '')
    if checkbox.isChecked():
        selected_params.append(param)
    else:
        selected_params.remove(param)


# noinspection PyTypeChecker
def save_profile():
    global selected_params, lst_profiles, configs
    if len(selected_params) == 0:
        QtWidgets.QMessageBox.warning(None, 'No params checked!', "You haven't checked any parameters! Please select at"
                                                                  " least one and try saving again")
        return

    profile_name, ok = QInputDialog.getText(None, 'Save profile', 'Enter the profile name:')
    if ok:
        lst_profiles.addItem(profile_name)
        configs['profiles'][profile_name] = selected_params
        save_configs()


# noinspection PyUnresolvedReferences
def delete_profile():
    global configs
    button_reply = QMessageBox.question(None, 'Delete profile', "Are you sure about deleting all selected profiles?", QMessageBox.Yes | QMessageBox.No,
                                        QMessageBox.No)
    if button_reply == QMessageBox.Yes:
        for selected_item in lst_profiles.selectedItems():
            lst_profiles.takeItem(lst_profiles.row(selected_item))
            del configs['profiles'][selected_item.text()]

        save_configs()


def execute_rvgl():
    global selected_params
    if configs['rvgl_found']:
        print('Launching RVGL')
        os.chdir(configs['rvgl_custom_path'])
        path = os.path.join(configs['rvgl_custom_path'], configs['rvgl_executable'])
        command = [path]
        for param in selected_params:
            command.append(param)
        subprocess.Popen(command)
        exit(0)
    else:
        look_for_rvgl()


def look_for_rvgl():
    global configs_loaded, configs
    if configs_loaded:
        return

    configs['rvgl_found'] = choose_rvgl_executable()

    if not configs['rvgl_found']:
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
            configs['rvgl_executable'] = f
            print("Setting RVGL executable to " + f)
            configs['rvgl_found'] = True
            save_configs()
            return True

    return False


def choose_custom_rvgl_location():
    options = QFileDialog.Options()
    options |= QFileDialog.ShowDirsOnly
    path = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose RVGL path", options=options)

    if path:
        configs['rvgl_custom_path'] = path
        print("Setting RVGL path to " + configs['rvgl_custom_path'])
        choose_rvgl_executable(path=configs['rvgl_custom_path'])


def save_configs():
    global configs
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
            print('Configs loaded')
    else:
        # First Run!
        # We need to create the empty profiles dictionary
        configs['profiles'] = {}


if __name__ == '__main__':
    load_configs()
    look_for_rvgl()

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    prog = RVGLAssistantProgram(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())
