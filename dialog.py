# Storing Dialog files.

from typing import Optional
from aqt.qt import QDialog, QWidget, Qt
from .ui.welcome import Ui_Dialog as WelcomeUI
from .ui.settings import Ui_Dialog as SettingsUI
from .config import Settings
from .config import MODELS

class WelcomeDialog(QDialog):

    def __init__(self, show_modal: bool = True, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.form = WelcomeUI()
        self.form.setupUi(self)
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.form.checkBox.setChecked(show_modal)
        
class SettingsDialog(QDialog):

    def __init__(self, settings: Settings):
        super().__init__()
        self.form = SettingsUI()
        self.form.setupUi(self)
        self.settings = settings

    def open(self):
        """Load settings and show the dialog."""
        self.load_from_config()
        super().open()

    def load_from_config(self):

        # Load non-platform-specific settings
        self.form.keySequenceEdit.setKeySequence(str(self.settings.shortcut_clear_current_card))
        self.form.keySequenceEdit_2.setKeySequence(str(self.settings.shortcut_clear_all_cards))
        self.form.keySequenceEdit_3.setKeySequence(str(self.settings.shortcut_include_exclude))
        self.form.keySequenceEdit_4.setKeySequence(str(self.settings.shortcut_pause))
        self.form.checkBox.setChecked(bool(self.settings.clear_cache_on_reviewer_end))

        # Set the excluded types.
        self.form.listWidget.clear()
        self.form.listWidget.addItems([str(item) for item in self.settings.exclude_note_types])

        # Set the platform dropdown. This must be done last, as it triggers the
        # `update_models` signal, which populates all platform-specific fields.
        platform_index = int(self.settings.platform_index)
        self.form.platformSelect.setCurrentIndex(platform_index)

        # Now, explicitly load all platform-specific settings.
        # This ensures the dialog is fully populated on open, even though
        # setCurrentIndex also triggers an update.
        platform_settings = self.settings.platform_configs[platform_index]

        # Populate the model dropdown with the correct list of models first.
        self.form.modelComboBox.clear()
        self.form.modelComboBox.addItems(MODELS[platform_index])

        # Now, set the values for all platform-specific fields.
        self.form.APIKeyLineEdit.setText(platform_settings.get("api_key", ""))
        self.form.modelComboBox.setCurrentText(platform_settings.get("model", ""))
        self.form.textEdit.setText(platform_settings.get("context", ""))
        self.form.maxRendersLineEdit.setText(str(platform_settings.get("max_renders", 3)))
        self.form.retryCountLineEdit.setText(str(platform_settings.get("num_retries", 3)))
        self.form.retryDelayLineEdit.setText(str(platform_settings.get("retry_delay_seconds", 1.0)))
