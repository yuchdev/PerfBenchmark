from PyQt5.QtWidgets import QDialogButtonBox, QCheckBox, QDialog, QVBoxLayout

DEFAULT_SETTINGS = {
    "rewrite_database": False
}


class SettingsWidget(QDialog):
    """
    Widget representing modal window Settings
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        # Add setting for "Rewrite Database on Startup"
        self.rewrite_database_checkbox = QCheckBox("Rewrite Database on Startup")
        layout.addWidget(self.rewrite_database_checkbox)

        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_settings(self):
        """
        Get current settings
        """
        settings = {"rewrite_database": self.rewrite_database_checkbox.isChecked()}
        return settings

    def set_settings(self, settings):
        """
        Set settings
        """
        self.rewrite_database_checkbox.setChecked(settings.get("rewrite_database", False))
