# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settingsrgRXMC.ui'
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
        Dialog.resize(441, 699)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayoutWidget = QWidget(Dialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 421, 680))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")

        self.verticalLayout.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.label_5 = QLabel(self.verticalLayoutWidget)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setOpenExternalLinks(True)

        self.verticalLayout.addWidget(self.label_5)

        self.verticalSpacer_6 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_6)

        self.label_3 = QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_3)

        self.formLayout_3 = QFormLayout()
        self.formLayout_3.setObjectName(u"formLayout_3")
        self.clearCurrentCardFromCacheLabel = QLabel(self.verticalLayoutWidget)
        self.clearCurrentCardFromCacheLabel.setObjectName(u"clearCurrentCardFromCacheLabel")

        self.formLayout_3.setWidget(0, QFormLayout.LabelRole, self.clearCurrentCardFromCacheLabel)

        self.keySequenceEdit = QKeySequenceEdit(self.verticalLayoutWidget)
        self.keySequenceEdit.setObjectName(u"keySequenceEdit")

        self.formLayout_3.setWidget(0, QFormLayout.FieldRole, self.keySequenceEdit)

        self.clearAllCardsFromCacheLabel = QLabel(self.verticalLayoutWidget)
        self.clearAllCardsFromCacheLabel.setObjectName(u"clearAllCardsFromCacheLabel")

        self.formLayout_3.setWidget(1, QFormLayout.LabelRole, self.clearAllCardsFromCacheLabel)

        self.keySequenceEdit_2 = QKeySequenceEdit(self.verticalLayoutWidget)
        self.keySequenceEdit_2.setObjectName(u"keySequenceEdit_2")

        self.formLayout_3.setWidget(1, QFormLayout.FieldRole, self.keySequenceEdit_2)

        self.excludeUnexcludeCurrentCardTypeLabel = QLabel(self.verticalLayoutWidget)
        self.excludeUnexcludeCurrentCardTypeLabel.setObjectName(u"excludeUnexcludeCurrentCardTypeLabel")

        self.formLayout_3.setWidget(2, QFormLayout.LabelRole, self.excludeUnexcludeCurrentCardTypeLabel)

        self.keySequenceEdit_3 = QKeySequenceEdit(self.verticalLayoutWidget)
        self.keySequenceEdit_3.setObjectName(u"keySequenceEdit_3")

        self.formLayout_3.setWidget(2, QFormLayout.FieldRole, self.keySequenceEdit_3)


        self.verticalLayout.addLayout(self.formLayout_3)

        self.verticalSpacer_2 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        sizePolicy1.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_2)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.maxRendersLabel = QLabel(self.verticalLayoutWidget)
        self.maxRendersLabel.setObjectName(u"maxRendersLabel")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.maxRendersLabel)

        self.maxRendersLineEdit = QLineEdit(self.verticalLayoutWidget)
        self.maxRendersLineEdit.setObjectName(u"maxRendersLineEdit")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.maxRendersLineEdit)

        self.mistralAPIKeyLabel = QLabel(self.verticalLayoutWidget)
        self.mistralAPIKeyLabel.setObjectName(u"mistralAPIKeyLabel")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.mistralAPIKeyLabel)

        self.mistralAPIKeyLineEdit = QLineEdit(self.verticalLayoutWidget)
        self.mistralAPIKeyLineEdit.setObjectName(u"mistralAPIKeyLineEdit")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.mistralAPIKeyLineEdit)

        self.mistralModelLabel = QLabel(self.verticalLayoutWidget)
        self.mistralModelLabel.setObjectName(u"mistralModelLabel")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.mistralModelLabel)

        self.mistralModelLineEdit = QLineEdit(self.verticalLayoutWidget)
        self.mistralModelLineEdit.setObjectName(u"mistralModelLineEdit")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.mistralModelLineEdit)

        self.textEdit = QTextEdit(self.verticalLayoutWidget)
        self.textEdit.setObjectName(u"textEdit")

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.textEdit)

        self.contextLabel = QLabel(self.verticalLayoutWidget)
        self.contextLabel.setObjectName(u"contextLabel")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.contextLabel)

        self.pauseDynamicCardGeneration = QLabel(self.verticalLayoutWidget)
        self.pauseDynamicCardGeneration.setObjectName(u"excludeUnexcludeCurrentCardTypeLabel_2")

        self.formLayout_3.setWidget(3, QFormLayout.LabelRole, self.pauseDynamicCardGeneration)

        self.keySequenceEdit_4 = QKeySequenceEdit(self.verticalLayoutWidget)
        self.keySequenceEdit_4.setObjectName(u"keySequenceEdit_4")

        self.formLayout_3.setWidget(3, QFormLayout.FieldRole, self.keySequenceEdit_4)


        self.verticalLayout.addLayout(self.formLayout)

        self.verticalSpacer_3 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_3)

        self.label_6 = QLabel(self.verticalLayoutWidget)
        self.label_6.setObjectName(u"label_6")
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_6)

        self.checkBox = QCheckBox(self.verticalLayoutWidget)
        self.checkBox.setObjectName(u"checkBox")

        self.verticalLayout.addWidget(self.checkBox)

        self.verticalSpacer_4 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_4)

        self.label_4 = QLabel(self.verticalLayoutWidget)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)

        self.verticalLayout.addWidget(self.label_4)

        self.listWidget = QListWidget(self.verticalLayoutWidget)
        self.listWidget.setObjectName(u"listWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.listWidget.sizePolicy().hasHeightForWidth())
        self.listWidget.setSizePolicy(sizePolicy2)
        self.listWidget.setSortingEnabled(True)

        # Set up the function
        self.listWidget.itemDoubleClicked.connect(self.handleListWidgetDoubleClick)

        self.verticalLayout.addWidget(self.listWidget)

        self.verticalSpacer_5 = QSpacerItem(20, 5, QSizePolicy.Minimum, QSizePolicy.Fixed)

        self.verticalLayout.addItem(self.verticalSpacer_5)

        self.buttonBox = QDialogButtonBox(self.verticalLayoutWidget)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)

        QMetaObject.connectSlotsByName(Dialog)

        Dialog.adjustSize()
        Dialog.setFixedSize(Dialog.size())

    def handleListWidgetDoubleClick(self, item: QListWidgetItem):
        ctr = 0
        while ctr < self.listWidget.count():
            if self.listWidget.item(ctr) == item:
                self.listWidget.takeItem(ctr)
                print(f'Removed item {item}')
                break
            ctr = ctr + 1

    # setupUi
    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dynamic Cards Settings", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"<h1>Dynamic Cards Settings</h1>", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"<b>Keyboard Shortcuts</b>", None))
        self.clearCurrentCardFromCacheLabel.setText(QCoreApplication.translate("Dialog", u"Clear current card from cache", None))
        self.clearAllCardsFromCacheLabel.setText(QCoreApplication.translate("Dialog", u"Clear all cards from cache", None))
        self.excludeUnexcludeCurrentCardTypeLabel.setText(QCoreApplication.translate("Dialog", u"Exclude/unexclude current card type", None))
        self.pauseDynamicCardGeneration.setText(QCoreApplication.translate("Dialog", u"Pause dynamic card generation", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"<b>LLM Functionality</b>", None))
        self.maxRendersLabel.setText(QCoreApplication.translate("Dialog", u"Max renders", None))
        self.mistralAPIKeyLabel.setText(QCoreApplication.translate("Dialog", u"Mistral API key", None))
        self.mistralModelLabel.setText(QCoreApplication.translate("Dialog", u"Mistral model", None))
        self.contextLabel.setText(QCoreApplication.translate("Dialog", u"Context", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"<b>Review Behavior</b>", None))
        self.checkBox.setText(QCoreApplication.translate("Dialog", u"Clear cache on review end", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"<b>Excluded Note Types</b> (double-click entry to remove)", None))
        self.label_5.setText(QCoreApplication.translate("Dialog", u"<a href='https://github.com/Petronian/dynamic-cards'>Need usage instructions? Click here!</a>", None))

        __sortingEnabled = self.listWidget.isSortingEnabled()
        self.listWidget.setSortingEnabled(False)
        self.listWidget.setSortingEnabled(__sortingEnabled)

    # retranslateUi
