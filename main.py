# -*- coding: utf-8 -*-

import os
import yaml
import subprocess
import faulthandler
import io
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QFileDialog, QInputDialog, QListView, QListWidgetItem, QListWidget
from gui import Ui_MainWindow
from menu_bar import *
from models import Car

faulthandler.enable()
configs = {}
configs_loaded = False
selected_params = []
lst_profiles = ""
grid_cars = ""


class RVGLAssistantProgram(Ui_MainWindow):
    def __init__(self, window):
        global lst_profiles, grid_cars
        Ui_MainWindow.__init__(self)
        self.setupUi(window)

        # Handles the menubar items
        self.actionExit.triggered.connect(menu_action_exit)
        self.actionChange_RVGL_Path.triggered.connect(choose_custom_rvgl_location)

        # Handles the buttons
        self.btn_launch.clicked.connect(execute_rvgl)
        self.btn_save.clicked.connect(save_profile)

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
        grid_cars = self.tbl_cars


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
    path, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Choose RVGL path", "",
                                                    "All Files (*.*);", options=options)

    if path:
        configs['rvgl_custom_path'] = path
        print("Setting RVGL path to " + configs['rvgl_custom_path'])
        choose_rvgl_executable(path=configs['rvgl_custom_path'])


def save_configs():
    global configs
    with io.open('./assistant.yml', 'w', encoding='utf8') as outfile:
        yaml.dump(configs, outfile, default_flow_style=False, allow_unicode=True)
        print('Configs saved')


def load_profile_list():
    global lst_profiles
    if configs_loaded:
        for profile in configs['profiles']:
            lst_profiles.addItem(profile)


def load_first_profile():
    pass


def load_configs():
    global configs, configs_loaded
    # We first check if the config file exists
    config_file = Path("./assistant.yml")
    if config_file.is_file():
        with open("./assistant.yml", 'r') as ymlfile:
            configs = yaml.load(ymlfile)
            configs_loaded = True
            load_profile_list()
            load_first_profile()
            print('Configs loaded')
    else:
        # First Run!
        # We need to create the empty profiles dictionary
        configs['profiles'] = {}


def look_for_cars():
    grid_cars.setViewMode(QListView.IconMode)
    grid_cars.setIconSize(QtCore.QSize(128, 128))

    cars = []

    for file in os.listdir(configs['rvgl_custom_path'] + '/cars/'):
        if os.path.isdir(configs['rvgl_custom_path'] + '/cars/' + file):
            car_path = os.path.join(configs['rvgl_custom_path'] + '/gfx/', file)
            cars.append(Car(file, car_path))

    for car in cars:
        car_img = os.path.join(configs['rvgl_custom_path'], 'cars', car.car_name, 'carbox.bmp')
        if not os.path.isfile(car_img):
            car_img = os.path.join(configs['rvgl_custom_path'], 'gfx', 'bot_bat.bmp')

        item = QListWidgetItem()
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(car_img), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        item.setIcon(icon)
        item.setText(car.car_name)
        grid_cars.addItem(item)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()

    prog = RVGLAssistantProgram(MainWindow)

    load_configs()
    look_for_rvgl()
    look_for_cars()

    MainWindow.show()
    sys.exit(app.exec_())
