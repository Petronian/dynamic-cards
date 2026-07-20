# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'welcomemUQqLm.ui'
##
## Created by: Qt User Interface Compiler version 6.4.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from aqt.qt import *

class Ui_Dialog(object):
    def setupUi(self, Dialog: QDialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(560, 440)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(10, 10, 10, 10)
        self.scrollArea = QScrollArea(Dialog)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setFrameShape(QFrame.Shape.NoFrame)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.scrollAreaLayout.setObjectName(u"scrollAreaLayout")
        self.scrollAreaLayout.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.scrollAreaWidgetContents)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setWordWrap(True)
        self.label_3.setOpenExternalLinks(True)
        self.label_3.setTextFormat(Qt.TextFormat.RichText)
        self.label_3.setTextInteractionFlags(
            Qt.TextInteractionFlag.LinksAccessibleByMouse | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.scrollAreaLayout.addWidget(self.label_3)
        self.scrollAreaLayout.addStretch(1)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout.addWidget(self.scrollArea)

        self.checkBox = QCheckBox(Dialog)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.buttonBox = QDialogButtonBox(Dialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Close)
        self.buttonBox.setCenterButtons(False)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)
        self._fitToScreen(Dialog)
    # setupUi

    def _fitToScreen(self, Dialog: QDialog):
        max_width = 900
        max_height = 700
        screen = Dialog.screen() or QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            max_width = min(max_width, int(available.width() * 0.9))
            max_height = min(max_height, int(available.height() * 0.9))

        Dialog.setMinimumSize(440, 320)
        Dialog.setMaximumSize(max_width, max_height)
        Dialog.adjustSize()
        Dialog.resize(min(Dialog.width(), max_width), min(Dialog.height(), max_height))

    # Edit once the Settings menu is created.
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Welcome", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"<h1>Welcome to Dynamic Cards!</h1>This extension aims to allow users to memorize card concepts, not card wording, by changing the wording of cards slightly upon each review of the card. Here's how it works:<ol><li>Review any card.</li><li>Dynamic Cards will automatically reword the card for the next review.</li><li>Once the maximum number of rewordings are achieved, rewordings will recycle.</li></ol>That's it! Once the following steps are completed, the extension should begin working automatically:<ol><li>Make a free <a href='https://console.mistral.ai/'>Mistral AI account.</a></li><li>Generate a Mistral API token and enter it in the <i>Tools > Dynamic Cards</i> menu.</li></ol>This plugin has several additional features for ease of use. <b>For full usage instructions, please see <a href='https://github.com/Petronian/dynamic-cards'>here.</a></b>", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Show this message on every startup", None))
    # retranslateUi