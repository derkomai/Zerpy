from pyqtspinner.spinner import WaitingSpinner
from PyQt5.QtCore import Qt, QSize, QRegExp
from PyQt5.QtGui import QColor, QFont, QIcon, QValidator, QRegExpValidator, QBrush
from PyQt5.QtWidgets import (QLabel, QMessageBox, QLineEdit, QWidget, QStackedWidget,
                            QPushButton, QVBoxLayout, QHBoxLayout, QTableWidget,
                            QHeaderView, QTableWidgetItem, QMenu, QApplication)

hex_colors = {'grey': '#353535',
              'green': '#c4df9b',
              'red': '#f6989d',
              'blue': '#0066cc',
              'white95': '#f2f2f2'}


class TransactionsWidget(QStackedWidget):

    sendButtonEnableConditions = [False, False]
    spinner = None

    def __init__(self, controller, refreshSignal):
        super().__init__()
        self.controller = controller
        self.refreshSignal = refreshSignal

        # Balance label
        balaceLabel = QLabel()
        balaceLabel.setText('Balance')
        balaceLabel.setAlignment(Qt.AlignCenter)

        # Balance amount label
        self.balaceAmountLabel = QLabel()
        self.balaceAmountLabel.setText(f'{self.controller.getBalance()} XRP')
        self.balaceAmountLabel.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(20)
        self.balaceAmountLabel.setFont(font)

        # Balance layout
        balanceLayout = QVBoxLayout()
        balanceLayout.addWidget(balaceLabel)
        balanceLayout.addWidget(self.balaceAmountLabel)
        balanceLayout.setContentsMargins(0, 10, 0, 10)

        # Transactions label
        transactionsLabel = QLabel('Transactions')
        transactionsLabel.setAlignment(Qt.AlignCenter)
        transactionsLabel.setContentsMargins(0, 0, 0, 10)

        # Transactions table
        self.tableWidget = QTableWidget()
        self.tableWidget.setColumnCount(1)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.horizontalHeader().setVisible(False)
        self.tableWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.tableWidget.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.populateTable()
        monofont = QFont()
        monofont.setFamily("Courier New")
        monofont.setPointSize(10)
        self.tableWidget.setFont(monofont)

        # Transactions layout
        transactionsLayout = QVBoxLayout()
        transactionsLayout.addWidget(transactionsLabel)
        transactionsLayout.addWidget(self.tableWidget)
        transactionsLayout.setContentsMargins(0, 0, 0, 0)

        # Send label A
        sendLabelA = QLabel('Send')
        sendLabelA.setAlignment(Qt.AlignCenter)

        # Send amount
        self.sendAmount = QLineEdit()
        self.sendAmount.setAlignment(Qt.AlignCenter)
        self.sendAmount.setFont(monofont)
        self.sendAmount.setPlaceholderText('Amount')
        validator = QRegExpValidator(QRegExp(r'^[0-9]+\.?[0-9]{0,6}$'))
        self.sendAmount.setValidator(validator)
        self.sendAmount.textChanged.connect(self.check_state)
        self.sendAmount.textChanged.emit(self.sendAmount.text())
        self.sendAmount.textChanged.connect(lambda: self.on_text_changed(0))

        # Send label B
        sendLabelB = QLabel('XRP to')
        sendLabelB.setAlignment(Qt.AlignCenter)

        # Send address
        self.sendAddress = QLineEdit()
        self.sendAddress.setAlignment(Qt.AlignCenter)
        self.sendAddress.setFont(monofont)
        self.sendAddress.setPlaceholderText('Address')
        validator = QRegExpValidator(QRegExp('^r[A-HJ-NP-Za-km-z1-9]{24,34}$'))
        self.sendAddress.setValidator(validator)
        self.sendAddress.textChanged.connect(self.check_state)
        self.sendAddress.textChanged.emit(self.sendAmount.text())
        self.sendAddress.textChanged.connect(lambda: self.on_text_changed(1))

        # Send tag
        self.sendTag = QLineEdit()
        self.sendTag.setAlignment(Qt.AlignCenter)
        self.sendTag.setFont(monofont)
        self.sendTag.setPlaceholderText('Tag')
        validator = QRegExpValidator(QRegExp(r'^\d*$'))
        self.sendTag.setValidator(validator)
        self.sendTag.textChanged.connect(self.check_state)

        # Send button
        self.sendButton = QPushButton()
        self.sendButton.setMaximumSize(40, 40)
        sendIcon = QIcon.fromTheme("mail-send")
        self.sendButton.setIcon(sendIcon)
        self.sendButton.setIconSize(QSize(24,24))
        self.sendButton.clicked.connect(self.on_send_clicked)
        self.sendButton.setEnabled(False)

        # Send layout
        sendLayout = QHBoxLayout()
        sendLayout.addWidget(sendLabelA)
        sendLayout.addWidget(self.sendAmount, 2)
        sendLayout.addWidget(sendLabelB)
        sendLayout.addWidget(self.sendAddress, 4)
        sendLayout.addWidget(self.sendTag, 1)
        sendLayout.addWidget(self.sendButton)
        sendLayout.setContentsMargins(0, 0, 0, 0)

        # Info layout
        balanceWidget = QWidget()
        balanceWidget.setLayout(balanceLayout)
        transactionsWidget = QWidget()
        transactionsWidget.setLayout(transactionsLayout)
        sendWidget = QWidget()
        sendWidget.setLayout(sendLayout)

        self.infoLayout = QVBoxLayout()
        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.addWidget(balanceWidget)
        self.infoLayout.addWidget(transactionsWidget)
        self.infoLayout.addWidget(sendWidget)

        # Waiting spinner
        self.spinner = WaitingSpinner(self)
        self.spinnerLayout = QVBoxLayout()
        self.spinnerLayout.addWidget(self.spinner)
        self.spinner.start()

        # Stacked widget
        infoWidget = QWidget()
        infoWidget.setLayout(self.infoLayout)

        spinnerWidget = QWidget()
        spinnerWidget.setLayout(self.spinnerLayout)

        self.setContentsMargins(0, 0, 0, 0)
        self.addWidget(infoWidget)
        self.addWidget(spinnerWidget)
        self.setCurrentIndex(0)

    def switchWidget(self):
        if self.currentIndex() == 0:
            self.setCurrentIndex(1)
        else:
            self.setCurrentIndex(0)

    def on_send_clicked(self):
        confirmAlert = QMessageBox()
        confirmAlert.setWindowTitle('Send payment')
        confirmAlert.setText(f'You are about to send {self.sendAmount.text()} XRP to:\n'
                             f'Address: {self.sendAddress.text()}\n'
                             f'Destination tag: {self.sendTag.text() if self.sendTag.text() else "None"}\n'
                              'Continue?')
        confirmAlert.setIcon(QMessageBox.Warning)
        confirmAlert.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        result = confirmAlert.exec_()

        if result == QMessageBox.Ok:
            payment = self.controller.sendPayment(self.sendAmount.text(),
                                                  self.sendAddress.text(),
                                                  self.sendTag.text())
            alert = QMessageBox()
            alert.setWindowTitle('Send payment')
            if payment['status'] == 'ok':
                alert.setText('Payment sent!')
                alert.setIcon(QMessageBox.Information)
                self.sendAmount.setText('')
                self.sendAddress.setText('')
                self.sendTag.setText('')
                self.refreshSignal.emit()
            else:
                alert.setWindowTitle('Something went wrong')
                alert.setText(payment['message'])
                alert.setIcon(QMessageBox.Critical)
            alert.exec_()

    def populateTable(self):
        txs = self.controller.getFormattedTransactions()
        self.tableWidget.setRowCount(len(txs))

        for i in range(len(txs)):
            item = QTableWidgetItem(txs[i])
            if '+' in txs[i]:
                item.setForeground(QBrush(QColor(hex_colors['green'])))
            elif '-' in txs[i]:
                item.setForeground(QBrush(QColor(hex_colors['red'])))
            else:
                item.setForeground(QBrush(QColor(hex_colors['white'])))
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
            self.tableWidget.setItem(i, 0, item)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        openAction = menu.addAction('Open transaction in browser')
        copyAddressAction = menu.addAction('Copy destination address')
        copyIDAction = menu.addAction('Copy transaction ID')
        gp = event.globalPos()
        action = menu.exec_(gp)
        vp_pos = self.tableWidget.viewport().mapFromGlobal(gp)
        row = self.tableWidget.rowAt(vp_pos.y())

        if action == openAction:
            self.controller.openTransactionInBrowser(row)
        elif action == copyAddressAction:
            txAddress = self.controller.getTxAddressByIndex(row)
            QApplication.clipboard().setText(txAddress)
        elif action == copyIDAction:
            txID = self.controller.getTxIDByIndex(row)
            QApplication.clipboard().setText(txID)

    def check_state(self, *args, **kwargs):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if not sender.text():
            color = hex_colors['white95']
        else:
            if state == QValidator.Acceptable:
                color = hex_colors['green']
            else:
                color = hex_colors['red']
        sender.setStyleSheet('QLineEdit { color: %s }' % color)

    def on_text_changed(self, i: int):
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            self.sendButtonEnableConditions[i] = True
        else:
            self.sendButtonEnableConditions[i] = False

        if False not in self.sendButtonEnableConditions:
            self.sendButton.setEnabled(True)
            self.sendButton.setStyleSheet(f"background-color: {hex_colors['blue']}")
        else:
            self.sendButton.setEnabled(False)
            self.sendButton.setStyleSheet(f"background-color: {hex_colors['grey']}")

    def on_new_data(self):
        result = {'status': 'ok'}
        for data in [self.controller.account_info, self.controller.transactions]:
            if data['status'] == 'error':
                result['status'] = 'error'
                result['message'] = self.api.get_error_message(data)
                break

        if result['status'] == 'ok':
            self.balaceAmountLabel.setText(f'{self.controller.getBalance()} XRP')
            self.populateTable()
        else:
            confirmAlert = QMessageBox()
            confirmAlert.setWindowTitle('Something went wrong')
            confirmAlert.setText(result['message'])
            confirmAlert.setIcon(QMessageBox.Critical)
            confirmAlert.setStandardButtons(QMessageBox.Ok)
            confirmAlert.exec_()
