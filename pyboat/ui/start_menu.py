#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import (
    QCheckBox,
    QAction,
    QMainWindow,
    QApplication,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QMessageBox,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QGridLayout,
)
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtGui import QDoubleValidator


from pyboat.ui import util 
from pyboat.ui.data_viewer import DataViewer
from pyboat.ui.synth_gen import SynthSignalGen
from pyboat import __version__

# matplotlib settings
from matplotlib import rc

rc("text", usetex=False)  # better for the UI


doc_url = "https://github.com/tensionhead/pyBOAT/blob/master/README.md"


class MainWindow(QMainWindow):
    def __init__(self, debug):
        super().__init__()

        self.debug = debug

        self.nViewers = 0
        self.DataViewers = {}  # no Viewers yet
        self.initUI()
        
    def initUI(self):

        self.setGeometry(80, 100, 200, 50)
        self.setWindowTitle(f"pyBOAT {__version__}")

        # Actions for the menu - status bar
        main_widget = QWidget()
        # online help in lower left corner
        self.statusBar()

        quitAction = QAction("&Quit", self)
        quitAction.setShortcut("Ctrl+Q")
        quitAction.setStatusTip("Quit pyBOAT")
        quitAction.triggered.connect(self.close_application)

        openFile = QAction("&Load data", self)
        openFile.setShortcut("Ctrl+L")
        openFile.setStatusTip("Load data")
        openFile.triggered.connect(self.Load_and_init_Viewer)

        ImportMenu = QAction("&Import..", self)
        ImportMenu.setShortcut("Ctrl+I")
        ImportMenu.setStatusTip("Set import options")
        ImportMenu.triggered.connect(self.init_import_menu)
                
        go_to_settings = QAction("&Default Parameters", self)
        go_to_settings.setStatusTip("Change default analysis parameters")      
        go_to_settings.triggered.connect(self.open_settings_menu)
        
        go_to_doc = QAction("&Documentation..", self)
        go_to_doc.triggered.connect(self.open_doc_link)

        # --- the menu bar ---

        mainMenu = self.menuBar()
        mainMenu.setNativeMenuBar(False)

        fileMenu = mainMenu.addMenu("&File")
        fileMenu.addAction(openFile)
        fileMenu.addAction(ImportMenu)
        fileMenu.addAction(quitAction)

        settingsMenu = mainMenu.addMenu("&Preferences")
        settingsMenu.addAction(go_to_settings)
        
        helpMenu = mainMenu.addMenu("&Help")
        helpMenu.addAction(go_to_doc)

        

        # --- Import Data ---
        
        load_box = QGroupBox("Import Data")
        load_box_layout = QVBoxLayout()

        openFileButton = QPushButton("Open", self)
        openFileButton.setStatusTip(
            "Load a table directly, assumes a header is present!"
        )
        openFileButton.setStyleSheet("background-color: lightblue")
        
        openFileButton.clicked.connect(self.Load_and_init_Viewer)
        load_box_layout.addWidget(openFileButton)

        ImportButton = QPushButton("Import..", self)
        ImportButton.setStatusTip("Set import options")
        ImportButton.clicked.connect(self.init_import_menu)
        load_box_layout.addWidget(ImportButton)

        load_box.setLayout(load_box_layout)

        # --- SSG ---
        
        synsig_box = QGroupBox("Synthetic Signals")
        synsig_box_layout = QVBoxLayout()

        synsigButton = QPushButton("Start Generator", self)
        synsigButton.setStyleSheet("background-color: orange")
        synsigButton.setStatusTip("Start the synthetic signal generator")        
        synsigButton.clicked.connect(self.init_synsig_generator)

        # quitButton = QPushButton("Quit", self)
        # quitButton.clicked.connect(self.close_application)
        # quitButton.setMaximumWidth(50)

        synsig_box_layout.addStretch(1)
        synsig_box_layout.addWidget(synsigButton)
        synsig_box_layout.addStretch(1)
        synsig_box.setLayout(synsig_box_layout)

        # --- Main Layout ---
        
        main_layout = QHBoxLayout()
        main_layout.addWidget(load_box)
        main_layout.addWidget(synsig_box)

        # main_layout.addWidget(quitButton,1,1)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        self.show()

    def init_synsig_generator(self):

        if self.debug:
            print("function init_synsig_generator called..")

        self.ssg = SynthSignalGen(self.debug)

    def close_application(self):

        # no confirmation window
        if self.debug:
            appc = QApplication.instance()
            appc.closeAllWindows()
            return

        choice = QMessageBox.question(
            self,
            "Quitting",
            "Do you want to exit pyBOAT?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if choice == QMessageBox.Yes:
            print("Quitting ...")
            # sys.exit()
            appc = QApplication.instance()
            appc.closeAllWindows()
        else:
            pass

    def Load_and_init_Viewer(self):

        if self.debug:
            print("function Viewer_Ini called")

        # load a table directly
        df, err_msg = util.load_data(self.debug)

        if err_msg:
            self.error = util.MessageWindow(err_msg, "Loading error")
            return

        self.nViewers += 1
        # initialize new DataViewer with the loaded data
        self.DataViewers[self.nViewers] = DataViewer(
            data=df,
            pos_offset = self.nViewers * 20,
            debug=self.debug)

    def init_import_menu(self):

        self.imp_menu = ImportMenu(self, debug=self.debug)

    def open_settings_menu(self):

        self.settings_menu = SettingsMenu(self, debug=self.debug)
        
    def open_doc_link(self):

        QDesktopServices.openUrl(QUrl(doc_url))

        
class ImportMenu(QWidget):
    def __init__(self, parent, debug=False):
        super().__init__()

        self.parent = parent
        self.debug = debug
        self.DataViewers = {}  # no Viewers yet

        self.load_settings()
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Data Import Options")
        self.setGeometry(120, 150, 150, 50)

        config_w = QWidget()
        config_grid = QGridLayout()
        config_w.setLayout(config_grid)

        self.cb_use_ext = QCheckBox("Separator from extension")
        self.cb_use_ext.toggle()
        self.cb_use_ext.setToolTip(
            "Infer the column separator from the file extension like '.csv'"
        )
        self.cb_use_ext.stateChanged.connect(self.toggle_ext)
        self.sep_label = QLabel("Column separator")
        self.sep_label.setDisabled(True)
        self.sep_edit = QLineEdit()
        self.sep_edit.setDisabled(True)
        self.sep_edit.setToolTip("Leave empty for automatic detection")

        self.cb_header = QCheckBox("No header row present", self)
        self.cb_header.setToolTip("Assigns a numeric sequence as column names")
        self.cb_header.setChecked(False)

        self.cb_NaN = QCheckBox("Interpolate missing values")
        self.cb_NaN.setToolTip("Linear interpolate in between missing values")

        NaN_label = QLabel("Set missing values entry")
        self.NaN_edit = QLineEdit()
        tt = """ 
        The following values are interpreted as missing values per default: 
        ‘’, ‘#N/A’, ‘#N/A N/A’, ‘#NA’, ‘-1.#IND’, ‘-1.#QNAN’, 
        ‘-NaN’, ‘-nan’, ‘1.#IND’, ‘1.#QNAN’, ‘<NA>’, ‘N/A’, 
        ‘NA’, ‘NULL’, ‘NaN’, ‘n/a’, ‘nan’, ‘null’
        """
        self.NaN_edit.setToolTip(tt)

        config_grid.addWidget(self.cb_use_ext, 0, 0, 1, 2)
        config_grid.addWidget(self.sep_label, 1, 0)
        config_grid.addWidget(self.sep_edit, 1, 1)
        config_grid.addWidget(self.cb_header, 2, 0, 1, 2)
        config_grid.addWidget(self.cb_NaN, 3, 0, 1, 2)
        config_grid.addWidget(NaN_label, 4, 0)
        config_grid.addWidget(self.NaN_edit, 4, 1)

        OpenButton = QPushButton("Open", self)
        OpenButton.setStyleSheet("background-color: lightblue")
        OpenButton.setToolTip("Select an input file with the chosen settings..")
        OpenButton.clicked.connect(self.import_file)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(OpenButton)
        button_box.addStretch(1)
        button_w = QWidget()
        button_w.setLayout(button_box)

        main_layout = QVBoxLayout()
        main_layout.addWidget(config_w)
        main_layout.addWidget(button_w)

        # set main layout
        self.setLayout(main_layout)        
        self.show()

    def toggle_ext(self):

        self.sep_label.setDisabled(self.cb_use_ext.isChecked())
        self.sep_edit.setDisabled(self.cb_use_ext.isChecked())

    def import_file(self):

        """
        Reads the values from the config grid
        and prepares kwargs for the pandas read_... functions

        NaN interpolation is done here if requested
        """

        kwargs = {}

        if self.cb_header.isChecked():
            header = None  # pandas will assign numeric column names
        else:
            header = "infer"

        if not self.cb_use_ext.isChecked():

            sep = self.sep_edit.text()
            # empty field
            if sep == "":
                sep = None
            kwargs["sep"] = sep
            if self.debug:
                print(f"Separator is {sep}, with type {type(sep)}")

        NaN_value = self.NaN_edit.text()
        # empty field
        if NaN_value == "":
            NaN_value = None
        if self.debug:
            print(f"NaN value is {NaN_value}, with type {type(NaN_value)}")

        # assemble key-words for pandas read_... functions
        kwargs["header"] = header
        kwargs["na_values"] = NaN_value

        if self.debug:
            print(f"kwargs for load_data: {kwargs}")

        # -----------------------------------------------------
        df, err_msg = util.load_data(debug=self.debug, **kwargs)
        if err_msg:
            self.error = util.MessageWindow(err_msg, "Loading error")
            return
        # -----------------------------------------------------

        if self.cb_NaN.isChecked():

            N_NaNs = df.isna().to_numpy().sum()
            if N_NaNs > 0:
                msg = f"Found {N_NaNs} missing values in total\nlinearly interpolating through.."
                self.Interpolation = util.MessageWindow(msg, "NaN Interpolation")

            else:
                self.Interpolation = util.MessageWindow(
                    "No missing values found!", "NaN Interpolation"
                )

            name = df.name
            df = util.interpol_NaNs(df)
            df.name = name  # restore name

        # initialize new DataViewer with the loaded data
        self.parent.nViewers += 1        
        self.parent.DataViewers[self.parent.nViewers] = DataViewer(
            data=df,
            pos_offset=self.parent.nViewers * 20,
            debug=self.debug)
        
        self.close()

        
class SettingsMenu(QWidget):
    def __init__(self, parent, debug=False):
        super().__init__()

        self.parent = parent
        self.debug = debug
        self.DataViewers = {}  # no Viewers yet

        self.load_settings()
        self.initUI()

    def initUI(self):

        self.setWindowTitle("Set Default Parameters")
        self.setGeometry(150, 150, 150, 50)

        config_w = QWidget()
        config_grid = QGridLayout()
        config_w.setLayout(config_grid)

        sampling_label = QLabel("Sampling Interval")
        self.sampling_edit = QLineEdit()
        self.sampling_edit.setValidator(QDoubleValidator(0, 99999, 3))
        self.sampling_edit.setToolTip('How much time in between two recordings?')        
        time_label = QLabel("Time Unit")
        self.time_edit = QLineEdit()
        self.time_edit.setToolTip('Sets the time unit label')

        cut_off_label = QLabel("Cut-off Period")
        self.cut_off_edit = QLineEdit()
        self.cut_off_edit.setToolTip('Larger periods get removed by the sinc filter')
        
        wsize_label = QLabel("Window Size")
        self.wsize_edit = QLineEdit()
        self.wsize_edit.setToolTip('For amplitude envelope estimation')

        Tmin_label = QLabel("Smallest Period")
        self.Tmin_edit = QLineEdit()
        self.Tmin_edit.setToolTip('Lower period limit for the Wavelet transform')
        Tmax_label = QLabel("Highest Period")
        self.Tmax_edit = QLineEdit()
        self.Tmax_edit.setToolTip('Upper period limit for the Wavelet transform')
        nT_label = QLabel("Number of Periods")
        self.nT_edit = QSpinBox()
        self.nT_edit.setRange(0, 10000)        

        self.nT_edit.setToolTip('Spectral resolution on the period axis')

        pmax_label = QLabel("Maximal Power")
        self.pmax_edit = QLineEdit()
        self.pmax_edit.setToolTip('Scales the colormap of the spectra')

        # 1st column
        
        config_grid.addWidget(sampling_label, 0, 0)
        config_grid.addWidget(self.sampling_edit, 0, 1)
        
        config_grid.addWidget(time_label, 1, 0)
        config_grid.addWidget(self.time_edit, 1, 1)

        config_grid.addWidget(cut_off_label, 2, 0)
        config_grid.addWidget(self.cut_off_edit, 2, 1)

        config_grid.addWidget(wsize_label, 3, 0)
        config_grid.addWidget(self.wsize_edit, 3, 1)

        # 2nd column
        
        config_grid.addWidget(Tmin_label, 0, 2)
        config_grid.addWidget(self.Tmin_edit, 0, 3)

        config_grid.addWidget(Tmax_label, 1, 2)
        config_grid.addWidget(self.Tmax_edit, 1, 3)

        config_grid.addWidget(nT_label, 2, 2)
        config_grid.addWidget(self.nT_edit, 2, 3)

        config_grid.addWidget(pmax_label, 3, 2)
        config_grid.addWidget(self.pmax_edit, 3, 3)
        
        CancelButton = QPushButton("Cancel", self)
        CancelButton.setToolTip("Discard changes")
        CancelButton.clicked.connect(self.clicked_cancel)
                
        OkButton = QPushButton("Ok", self)
        OkButton.setToolTip("Approve changes")
        OkButton.clicked.connect(self.clicked_ok)

        button_box = QHBoxLayout()
        button_box.addStretch(1)
        button_box.addWidget(CancelButton)
        button_box.addWidget(OkButton)        
        button_box.addStretch(1)
        button_w = QWidget()
        button_w.setLayout(button_box)

        main_layout = QVBoxLayout()
        main_layout.addWidget(config_w)
        main_layout.addWidget(button_w)

        # set main layout
        self.setLayout(main_layout)
        self.show()

    def clicked_ok(self):

        ''' Retrieves all input fields '''

        value = util.retrieve_double_edit(self.sampling_edit)
        print(value, type(value))

        value = self.nT_edit.value()
        print(value, type(value))

        pass
    
    def clicked_cancel(self):
        self.close()
        
    def load_settings(self):
        
        self.settings = QSettings()

        # load defaults or restore values
        for key, value in util.default_par_dict.items():
            self.settings.value(key, value)
        
