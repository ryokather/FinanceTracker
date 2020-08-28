from app import *
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QPropertyAnimation, QRect, QEasingCurve, QDate
from PyQt5.QtGui import QPixmap

class UIFunctions(MainWindow):
    # UI function to toggle the sidebar menu. Minimized is the min width to still show sidebar icons
    def toggleMenu(self, maxWidth, enable):
        if enable:
            width = self.ui.left_menu.width()
            standard = maxWidth
            minimized = 70

            if width == maxWidth:
                newWidth = minimized
            else:
                newWidth = standard
            
            self.animation = QPropertyAnimation(self.ui.left_menu, b"maximumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(newWidth)
            self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
            self.animation.start()
    
    # Updates the dashboard spending widget specified by totalIncome and percentage. Also displays the correct trend based on the percentage
    def updateSpending(self, totalSpending: float=0.00, percentage: float=0.0):
        string1 = self.formatAmount(totalSpending)

        if percentage == 100: # prevMonth spending was 0
            string2 = "---%"
        else:
            if percentage < 0: # determine whether was percentage increase or decrease
                string2 = str(percentage) + "% decrease from last month"
            else:
                string2 = "+" + str(percentage) + "% increase from last month"
        self.ui.label_dbd_spendingAmt.setText(string1)
        self.ui.label_dbd_spendingPercentage.setText(string2)

        # Set correct pixmap based on percentage
        if percentage > 0:
            im = QPixmap("/Users/ryokather/Desktop/Coding/personalFinance/assets/increasingRed.png")
            self.ui.icon_dbd_spendingTrend.setPixmap(im)
        elif percentage < 0:
            im = QPixmap("/Users/ryokather/Desktop/Coding/personalFinance/assets/decreasingGreen.png")
            self.ui.icon_dbd_spendingTrend.setPixmap(im)
        else:
            im = QPixmap("")
            self.ui.icon_dbd_spendingTrend.setPixmap(im)

    # Updates the dashboard income widget specified by totalIncome and percentage. Also displays the correct trend based on the percentage
    def updateIncome(self, totalIncome: float=0.00, percentage: float=0.0):
        string1 = self.formatAmount(totalIncome)

        if percentage == 100: # prevMonth income was 0
            string2 = "---%"
        else:
            if percentage < 0: # determine whether was percentage increase or decrease
                string2 = str(percentage) + "% decrease from last month"
            else:
                string2 = "+" + str(percentage) + "% increase from last month"

        self.ui.label_dbd_incomeAmt.setText(string1)
        self.ui.label_dbd_incomePercentage.setText(string2)

        # Set correct pixmap based on percentage
        if percentage > 0:
            im = QPixmap("/Users/ryokather/Desktop/Coding/personalFinance/assets/increasingGreen.png")
            self.ui.icon_db_incomeTrend.setPixmap(im)
        elif percentage < 0:
            im = QPixmap("/Users/ryokather/Desktop/Coding/personalFinance/assets/decreasingRed.png")
            self.ui.icon_db_incomeTrend.setPixmap(im)
        else:
            im = QPixmap("")
            self.ui.icon_db_incomeTrend.setPixmap(im)

    # Function is called when an account has been renamed or deleted
    # Since the combo box displaying which account to display has been reset, selects account in the combo box if necessary
    def accountsChanged(self, oldAccName: str, newAccName: str):
        acc1 = acc2 = ""
        if newAccName == "None": # account is to be deleted, check if account is currently being displayed
            acc1 = self.ui.label_dbd_firstAccount.text()
            if acc1 == oldAccName:
                acc1 = "No account added or chosen"
            else:
                self.ui.comboBox_settings_acc1.setCurrentText(acc1)
            acc2 = self.ui.label_dbd_secondAccount.text()
            if acc2 == oldAccName:
                acc2 = ""
            else:
                self.ui.comboBox_settings_acc2.setCurrentText(acc2)
        else: # account name was edited, check if account is currently being displayed
            acc1 = self.ui.label_dbd_firstAccount.text()
            if acc1 == oldAccName:
                acc1 = newAccName
            self.ui.comboBox_settings_acc1.setCurrentText(acc1)
            acc2 = self.ui.label_dbd_secondAccount.text()
            if acc2 == oldAccName:
                acc2 = newAccName
            self.ui.comboBox_settings_acc2.setCurrentText(acc2)

        UIFunctions.updateAccountSummary(self, acc1, acc2)
    
    # UI function that updates the amount summary widget on the dashboard
    # TODO determine amounts of each account
    def updateAccountSummary(self, acc1: str, acc2: str):
        if acc1 == "No account added or chosen":
            amt1 = ""
        else:
            amt1 = "$0.00"
        
        if acc2 == "":
            amt2 = ""
        else:
            amt2 = "$0.00" 

        self.ui.label_dbd_firstAccount.setText(acc1)
        self.ui.label_dbd_secondAccount.setText(acc2)
        self.ui.label_dbd_firstAcctAmt.setText(amt1)
        self.ui.label_dbd_secondAcctAmt.setText(amt2)

    def getDashBoardAccounts(self) -> list:
        accounts = ["No account added or chosen",""]

        # only choose accounts from the list 
        if self.accounts:
            accounts[0] = self.accounts[0]
            self.ui.comboBox_settings_acc1.setCurrentText(accounts[0])
            if len(self.accounts) >= 2:
                accounts[1] = self.accounts[1]
                self.ui.comboBox_settings_acc1.setCurrentText(accounts[1])
                
        return accounts

    def analysisPage_updateSpendingInMonth(self, amount: float):
        formatted = self.formatAmount(amount)
        self.ui.label_analysisPg_spendingPerMonth.setText(formatted)

    def analysisPage_updateIncomeInMonth(self, amount: float):
        formatted = self.formatAmount(amount)
        self.ui.label_analysisPg_incomePerMonth.setText(formatted)

    def analysisPage_updateAvgSpending(self, avg: float):
        formatted = self.formatAmount(avg)
        self.ui.label_analysisPg_avgSpendingPerMonth.setText(formatted)

    def analysisPage_updateAvgIncome(self, avg: float):
        formatted = self.formatAmount(avg)
        self.ui.label_analysisPg_avgIncomePerMonth.setText(formatted)

    # Clears all account combo boxes
    def clearAllAccountComboBoxes(self):
        self.ui.comboBox_editAcct.clear()
        self.ui.comboBox_deleteAcct.clear()
        self.ui.comboBox_filter_accSelection.clear()
        self.ui.comboBox_add_accSelection.clear()
        self.ui.comboBox_settings_acc1.clear()
        self.ui.comboBox_settings_acc2.clear()

        UIFunctions.setupAccountComboBoxes(self)

    # Sets up the default items in the account combo boxes
    def setupAccountComboBoxes(self):
        self.ui.comboBox_add_accSelection.addItem("Select Account")
        self.ui.comboBox_filter_accSelection.addItem("All Accounts")
        self.ui.comboBox_editAcct.addItem("Select an account")
        self.ui.comboBox_deleteAcct.addItem("Select an account")
        self.ui.comboBox_settings_acc1.addItem("Select Account")
        self.ui.comboBox_settings_acc2.addItem("Select Account")
    
    ### TRANSACTIONS TABLE UI ###

    # Clears entire table
    def clearTable(self):
        self.ui.transactionsTable.clearContents()
        self.ui.transactionsTable.setRowCount(13)

    # Adds 13 empty rows into the table so empty rows are shown upon program starting
    def setupTable(self):
        for _ in range(13):
            rowCount = self.ui.transactionsTable.rowCount()
            self.ui.transactionsTable.insertRow(rowCount)
        UIFunctions.setTableColumnWidths(self)
        self.ui.transactionsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.transactionsTable.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.transactionsTable.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)

    def setTableColumnWidths(self):
        width = self.ui.transactionsTable.width()
        self.ui.transactionsTable.setColumnWidth(0, width * 0.10)
        self.ui.transactionsTable.setColumnWidth(1, width * 0.30)
        self.ui.transactionsTable.setColumnWidth(2, width * 0.22)
        self.ui.transactionsTable.setColumnWidth(3, width * 0.24)
        self.ui.transactionsTable.setColumnWidth(4, width * 0.12)

    # set min and max of each date edit box when program starts
    def setDateEdits(self, dateRange: tuple):
        self.ui.dateEdit_filter_fromDate.setDate(dateRange[0])
        self.ui.dateEdit_filter_toDate.setDate(dateRange[1])
    
    # Adds a single account to account combo boxes
    def addAccount_to_ui(self, account: str):
        self.ui.comboBox_add_accSelection.addItem(account)
        self.ui.comboBox_filter_accSelection.addItem(account)
        self.ui.comboBox_editAcct.addItem(account)
        self.ui.comboBox_deleteAcct.addItem(account)
        self.ui.comboBox_settings_acc1.addItem(account)
        self.ui.comboBox_settings_acc2.addItem(account)
    
    # Adds a list of accounts to account combo boxes
    def addAllAccounts_to_ui(self, accounts: list):
        self.ui.comboBox_filter_accSelection.addItems(accounts)
        self.ui.comboBox_add_accSelection.addItems(accounts)
        self.ui.comboBox_editAcct.addItems(accounts)
        self.ui.comboBox_deleteAcct.addItems(accounts)
        self.ui.comboBox_settings_acc1.addItems(accounts)
        self.ui.comboBox_settings_acc2.addItems(accounts)

    # Adds a name to the dashboard 
    def addName_to_ui(self, name: str):
        self.ui.lineEdit_enterName.setText(name)
        self.ui.label_welcomeMessage.setText(" Hello, " + name + "!")

    ### GETTER FUNCTIONS FROM UI ###

    def transactionsPage_getAccount_add(self) -> str:
        return self.ui.comboBox_add_accSelection.currentText()
    
    def accountsPage_getAccount_edit(self) -> str:
        return self.ui.comboBox_editAcct.currentText()

    def getKind_filter(self) -> str:
        return self.ui.comboBox_filter_kind.currentText()

    def getAccount_filter(self) -> str:
        return self.ui.comboBox_filter_accSelection.currentText()

    def getAccount_delete(self) -> str:
        return self.ui.comboBox_deleteAcct.currentText()

    def getCategory_filter(self) -> str:
        return self.ui.comboBox_filter_categorySelection.currentText()

    def getFromDate_filter(self) -> QDate:
        return self.ui.dateEdit_filter_fromDate.date()
    
    def getToDate_filter(self) -> QDate:
        return self.ui.dateEdit_filter_toDate.date()

    def analysisPage_spending_getMonth(self) -> str:
        return self.ui.comboBox_analysis_spendingPerMonth.currentText()

    def analysisPage_income_getMonth(self) -> str:
        return self.ui.comboBox_analysis_incomePerMonth.currentText()

    def analysisPage_spending_getRange(self) -> int:
        return self.ui.comboBox_analysis_spendingRange.currentIndex()
    
    def analysisPage_income_getRange(self) -> int:
        return self.ui.comboBox_analysis_incomeRange.currentIndex()
        
    def settingsPage_getAcc1(self) -> str:
        return self.ui.comboBox_settings_acc1.currentText()
    
    def settingsPage_getAcc2(self) -> str:
        return self.ui.comboBox_settings_acc2.currentText()

    def setFromDate_max(self, maxDate: QDate):
        self.ui.dateEdit_filter_fromDate.setMaximumDate(maxDate)

    def setToDate_min(self, minDate: QDate):
        self.ui.dateEdit_filter_toDate.setMinimumDate(minDate)

    # Updates the sorting by label on the transactions page
    def setSortLabel(self, sortMethod: str, ascending: bool):
        if ascending:
            self.ui.label_sortingBy.setText("Sorting by: " + sortMethod + " // " + "Ascending")
        else:
            self.ui.label_sortingBy.setText("Sorting by: " + sortMethod + " // " + "Descending")
    
    # Scrolls the table to the bottom of the table
    def scrollToBottom(self):
        self.ui.transactionsTable.scrollToBottom()

# An align delegate which is used to format the rightmost cell in the table to align right
class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignRight