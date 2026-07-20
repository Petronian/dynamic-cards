# Storing Dialog files.

from typing import Optional
from aqt.qt import QDialog, QWidget, Qt
from .ui.welcome import Ui_Dialog as WelcomeUI
from .ui.settings import Ui_Dialog as SettingsUI
from .config import Settings

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

    def show(self):
        super().show()
        self.load_from_config()

    def load_from_config(self):

        # Set all objects of simple datatypes.
        self.form.keySequenceEdit.setKeySequence(str(self.settings.shortcut_clear_current_card))
        self.form.keySequenceEdit_2.setKeySequence(str(self.settings.shortcut_clear_all_cards))
        self.form.keySequenceEdit_3.setKeySequence(str(self.settings.shortcut_include_exclude))
        self.form.keySequenceEdit_4.setKeySequence(str(self.settings.shortcut_pause))
        self.form.APIKeyLineEdit.setText(str(self.settings.api_key))
        self.form.maxRendersLineEdit.setText(str(self.settings.max_renders))
        self.form.textEdit.setText(str(self.settings.context))
        self.form.retryCountLineEdit.setText(str(self.settings.num_retries))
        self.form.retryDelayLineEdit.setText(str(self.settings.retry_delay_seconds))
        self.form.checkBox.setChecked(bool(self.settings.clear_cache_on_reviewer_end))
        self.form.platformSelect.setCurrentIndex(int(self.settings.platform_index))
        
        # This will trigger update_models, populating the model list.
        # Then we set the current model.
        self.form.modelComboBox.setCurrentText(str(self.settings.model))

        # Set the excluded types.
        self.form.listWidget.clear()
        self.form.listWidget.addItems([str(item) for item in self.settings.exclude_note_types])
