# Storing Dialog files.

from aqt.qt import QDialog
from .ui.welcome import Ui_Dialog as WelcomeUI
from .ui.settings import Ui_Dialog as SettingsUI
from .config import Settings

class WelcomeDialog(QDialog):

    def __init__(self, show_modal: bool = True):
        super().__init__()
        self.form = WelcomeUI()
        self.form.setupUi(self)
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
        self.form.mistralAPIKeyLineEdit.setText(str(self.settings.api_key))
        self.form.mistralModelLineEdit.setText(str(self.settings.model))
        self.form.maxRendersLineEdit.setText(str(self.settings.max_renders))
        self.form.textEdit.setText(str(self.settings.context))
        self.form.checkBox.setChecked(bool(self.settings.clear_cache_on_reviewer_end))

        # Set the excluded types.
        self.form.listWidget.clear()
        self.form.listWidget.addItems([str(item) for item in self.settings.exclude_note_types])
