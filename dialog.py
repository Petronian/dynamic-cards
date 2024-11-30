# Storing Dialog files.

from aqt.qt import QDialog
from .ui.welcome import Ui_Dialog as WelcomeUI

class WelcomeDialog(QDialog):

    def __init__(self):
        super().__init__()
        self._form = WelcomeUI()
        self._form.setupUi(self)