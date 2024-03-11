import json
import os.path

from PyQt5.QtWidgets import QDialogButtonBox, QCheckBox, QDialog, QVBoxLayout

DEFAULT_SETTINGS = {
    "rewrite_database": False
}


class SettingsWidget(QDialog):
    """
    Widget representing modal window Settings
    """

    def __init__(self, settings_file, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.settings_file = settings_file
        layout = QVBoxLayout()

        # Add setting for "Rewrite Database on Startup"
        self.rewrite_database_checkbox = QCheckBox("Rewrite Database on Startup")
        layout.addWidget(self.rewrite_database_checkbox)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        # noinspection PyUnresolvedReferences
        button_box.accepted.connect(self.write_settings)
        # noinspection PyUnresolvedReferences
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)
        self.load_settings()

    def load_settings(self):
        """
        Load settings from file
        """
        print('SettingsWidget.load_settings()')
        # Create settings file if it does not exist
        if not os.path.isfile(self.settings_file):
            with open(self.settings_file, 'w') as file:
                print(f'Created settings file: {self.settings_file} with default settings')
                json.dump(DEFAULT_SETTINGS, file)

        # Load settings from file
        with open(self.settings_file, 'r') as file:
            settings = json.load(file)
            print(f'Loaded settings: {settings} from {self.settings_file}')
            self.rewrite_database_checkbox.setChecked(settings["rewrite_database"])

    def write_settings(self):
        """
        Write settings to file
        """
        print('SettingsWidget.write_settings()')
        settings = {
            "rewrite_database": self.rewrite_database_checkbox.isChecked()
        }

        with open(self.settings_file, 'w') as file:
            json.dump(settings, file)
            print(f'Saved settings: {settings} to {self.settings_file}')

        self.accept()
