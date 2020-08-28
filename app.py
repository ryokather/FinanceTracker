from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import sys
from datetime import date, datetime
import pandas as pd
import numpy as np

from appModules import *

import db

class MainWindow(QMainWindow):
    MAP_TABLE_TO_SORT = {0: "Date", 1: "Merchant", 2: "Account", 3: "Category", 4: "Amount"}
    INDEX_TO_MONTHRANGE = {0: 3, 1: 6, 2: 12}
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = Ui_FinanceApp()
        self.ui.setupUi(self)

        # SET UP DEFAULT LOOK OF TRANSACTIONS TABLE
        UIFunctions.setupTable(self)

        #############################
        # START ——— Widget Functions 
        #############################

        ### START ——— ACCOUNTS PAGE ###
        
        # GET ACCOUNT TO ADD FROM LINE EDIT
        def getAccountToAdd():
            account = self.ui.lineEdit_addAcct.text()
            self.ui.lineEdit_addAcct.setText("Enter the name of the account")
            self.addAccount(account)
            self.ui.lineEdit_addAcct.clearFocus()

        self.ui.lineEdit_addAcct.returnPressed.connect(getAccountToAdd)
        
        # GET ACCOUNT TO EDIT FROM COMBO BOX AND LINE EDIT
        def getAccountToEdit():
            accountToEdit = UIFunctions.accountsPage_getAccount_edit(self)
            newAccountName = self.ui.lineEdit_editAcct.text()

            # Do nothing if no account was selected
            if accountToEdit == "Select an account" or accountToEdit == newAccountName:
                return
            self.updateAccount(accountToEdit, newAccountName)
            self.ui.lineEdit_editAcct.clearFocus()

        self.ui.lineEdit_editAcct.returnPressed.connect(getAccountToEdit)
        
        # GET ACCOUNT TO DELETE FROM COMBO BOX
        def deleteAccountButtonClicked():
            accToDelete = UIFunctions.getAccount_delete(self)

            # Do nothing if no account was selected
            if accToDelete == "Select an account":
                return
            self.deleteAccount(accToDelete)
        self.ui.pushButton_deleteAccount.clicked.connect(deleteAccountButtonClicked)

        ### END ————— ACCOUNTS PAGE ### 

        ### START ——— TRANSACTIONS PAGE ###

        # DETECTS WHEN A HEADER IN THE TABLE WAS PRESSED AND DETERMINES CORRESPONDING SORT METHOD
        def headerPressed(index):
            if self.selectedHeader == index:
                self.header_ascending = not self.header_ascending
            else:
                self.selectedHeader = index
                self.header_ascending = True
            self.displayed_df = self.sortDataFrame(self.displayed_df)
            self.fillTable(self.displayed_df)
            UIFunctions.setSortLabel(self, self.MAP_TABLE_TO_SORT[index], self.header_ascending)

        self.ui.transactionsTable.horizontalHeader().sectionClicked.connect(headerPressed)

        # GET FILE FROM LINE EDIT
        def getTransactionInput():
            file = self.ui.lineEdit_fileInput.text()
            self.ui.lineEdit_fileInput.setText("Enter the path and name of csv file")
            if file.lower().startswith("everything from"): # short cut to read multiple csv files at once
                self.grabMultipleCSV(file.split(" ")[-1])
            else:
                self.readCSVFile(file)
            self.ui.lineEdit_fileInput.clearFocus()

        self.ui.lineEdit_fileInput.returnPressed.connect(getTransactionInput)

        # CONNECT FILTER WIDGETS TO FILTER FUNCTION
        self.ui.comboBox_filter_kind.currentTextChanged.connect(self.filterDataFrame)
        self.ui.comboBox_filter_accSelection.currentTextChanged.connect(self.filterDataFrame)
        self.ui.comboBox_filter_categorySelection.currentTextChanged.connect(self.filterDataFrame)
        self.ui.dateEdit_filter_fromDate.editingFinished.connect(self.filterDataFrame)
        self.ui.dateEdit_filter_toDate.editingFinished.connect(self.filterDataFrame)
        
        ### END ————— TRANSACTIONS PAGE ### 

        ### START ——— ANALYSIS PAGE ###

        def analysisPage_spending_monthChosen():
            month = UIFunctions.analysisPage_spending_getMonth(self)
            if month == "Select Month":
                UIFunctions.analysisPage_updateSpendingInMonth(self, 0)
            else:
                amount = AnalysisFunctions.getSpendingInMonth(self, month)
                UIFunctions.analysisPage_updateSpendingInMonth(self, amount)

        def analysisPage_income_monthChosen():
            month = UIFunctions.analysisPage_income_getMonth(self)
            if month == "Select Month":
                UIFunctions.analysisPage_updateIncomeInMonth(self, 0)
            else:
                amount = AnalysisFunctions.getIncomeInMonth(self, month)
                UIFunctions.analysisPage_updateIncomeInMonth(self, amount)
        
        self.ui.comboBox_analysis_incomePerMonth.currentTextChanged.connect(analysisPage_income_monthChosen)
        self.ui.comboBox_analysis_spendingPerMonth.currentTextChanged.connect(analysisPage_spending_monthChosen)
        
        # set combo boxes to 6 months
        self.ui.comboBox_analysis_incomeRange.setCurrentIndex(1)
        self.ui.comboBox_analysis_spendingRange.setCurrentIndex(1)

        def spendingRangeChanged():
            index = UIFunctions.analysisPage_spending_getRange(self)
            AnalysisFunctions.updateSpendingTab(self, self.INDEX_TO_MONTHRANGE[index])

        self.ui.comboBox_analysis_spendingRange.currentTextChanged.connect(spendingRangeChanged)

        def incomeRangeChanged():
            index = UIFunctions.analysisPage_income_getRange(self)
            AnalysisFunctions.updateIncomeTab(self, self.INDEX_TO_MONTHRANGE[index])

        self.ui.comboBox_analysis_incomeRange.currentTextChanged.connect(incomeRangeChanged)


        ### END ————— ANALYSIS PAGE ###

        ### START ——— HELP PAGE ###

        ### END ————— HELP PAGE ###
         
        ### START ——— SETTINGS PAGE ###

        # GETS ENTERED NAME
        def getEnteredName():
            name = self.ui.lineEdit_enterName.text()
            self.addName(name)
            self.ui.lineEdit_enterName.clearFocus()

        self.ui.lineEdit_enterName.returnPressed.connect(getEnteredName)

        # GETS ACCOUNTS CHOSEN TO DISPLAY ON THE DASHBOARD
        def dbd_accountsChosen():
            acc1 = UIFunctions.settingsPage_getAcc1(self)
            acc2 = UIFunctions.settingsPage_getAcc2(self)

            if acc1 == "Select Account":
                acc1 = "No account added or chosen"
            if acc2 == "Select Account":
                acc2 = ""
            
            # only update if there is more than just select account -> resolves issue when function is called when program updates combo boxes rather than the user
            if self.ui.comboBox_settings_acc1.count() > 1: 
                UIFunctions.updateAccountSummary(self, acc1, acc2)

        self.ui.comboBox_settings_acc1.currentTextChanged.connect(dbd_accountsChosen)
        self.ui.comboBox_settings_acc2.currentTextChanged.connect(dbd_accountsChosen)

        ### END ————— SETTINGS PAGE ### 

        # TOGGLE SIDE MENU
        self.ui.menuToggle_button.clicked.connect(lambda: UIFunctions.toggleMenu(self, 200, True))
        
        # SET INITIAL VIEW TO DASHBOARD
        self.ui.stackedWidget.setCurrentWidget(self.ui.dashboardPage)
        self.ui.dashboardButton.setChecked(True)
        self.ui.accountsButton.setChecked(False)
        self.ui.transactionButton.setChecked(False)
        self.ui.analysisButton.setChecked(False)

        # SET UP PAGES — uncheck other buttons
        def dashboardButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.dashboardPage)
            self.ui.dashboardButton.setChecked(True)
            self.ui.accountsButton.setChecked(False)
            self.ui.transactionButton.setChecked(False)
            self.ui.analysisButton.setChecked(False)
            self.ui.helpButton.setChecked(False)
            self.ui.settingsButton.setChecked(False)

        def accountsButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.accountsPage)
            self.ui.dashboardButton.setChecked(False)
            self.ui.transactionButton.setChecked(False)
            self.ui.analysisButton.setChecked(False)
            self.ui.helpButton.setChecked(False)
            self.ui.settingsButton.setChecked(False)
        
        def transactionsButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.transactionsPage)
            self.ui.dashboardButton.setChecked(False)
            self.ui.accountsButton.setChecked(False)
            self.ui.analysisButton.setChecked(False)
            self.ui.helpButton.setChecked(False)
            self.ui.settingsButton.setChecked(False)

        def analysisButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.analysisPage)
            self.ui.dashboardButton.setChecked(False)
            self.ui.accountsButton.setChecked(False)
            self.ui.transactionButton.setChecked(False)
            self.ui.helpButton.setChecked(False)
            self.ui.settingsButton.setChecked(False)

        def helpButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.helpPage)
            self.ui.dashboardButton.setChecked(False)
            self.ui.accountsButton.setChecked(False)
            self.ui.transactionButton.setChecked(False)
            self.ui.analysisButton.setChecked(False)
            self.ui.settingsButton.setChecked(False)
        
        def settingsButtonClicked():
            self.ui.stackedWidget.setCurrentWidget(self.ui.settingsPage)
            self.ui.dashboardButton.setChecked(False)
            self.ui.accountsButton.setChecked(False)
            self.ui.transactionButton.setChecked(False)
            self.ui.analysisButton.setChecked(False)
            self.ui.helpButton.setChecked(False)
        
        self.ui.dashboardButton.clicked.connect(dashboardButtonClicked)
        self.ui.accountsButton.clicked.connect(accountsButtonClicked)
        self.ui.transactionButton.clicked.connect(transactionsButtonClicked)
        self.ui.analysisButton.clicked.connect(analysisButtonClicked)
        self.ui.helpButton.clicked.connect(helpButtonClicked)
        self.ui.settingsButton.clicked.connect(settingsButtonClicked)

        # CONNECT HOME BUTTON TO DASHBOARD
        self.ui.toolButton_home.clicked.connect(dashboardButtonClicked)

        ###########################
        # END ——— Widget Functions
        ###########################
        
        # SHOW ———— Main Window
        self.show()

        # Variables
        self.df = pd.DataFrame() # Master dataframe that stores all the transactions regardless of filters
        self.displayed_df = pd.DataFrame() # Currently displayed dataframe
        self.fromDate = self.convert_dateTime_to_QDate(date.today())
        self.toDate = self.convert_dateTime_to_QDate(date.today())
        
        # By default sorts by date in ascending order
        self.header_ascending = True
        self.selectedHeader = 0

        # Sets up rest of program - loads accounts into ui, transactions into dataframe, and sets up dashboard
        self.loadAccounts()
        self.loadName()
        self.df = self.loadTransactions() # default sorts it in chronological ascending order
        self.displayed_df = self.df
        self.fillTable(self.df)
        UIFunctions.scrollToBottom(self)
        UIFunctions.setDateEdits(self, self.ensureDateRange(self.df))
        self.updateDashboard()
        self.updateAnalysisPage()
        
    # Sets up the dashboard page
    # TODO Once ability to read balances from spreadsheets is completed, update correct balances on the dashboard
    def updateDashboard(self):
        # Set up account summary
        accounts = UIFunctions.getDashBoardAccounts(self)
        UIFunctions.updateAccountSummary(self, accounts[0], accounts[1])
        AnalysisFunctions.updateTotalSpendingAndIncome(self)

    def updateAnalysisPage(self):
        AnalysisFunctions.updateTabs(self)
        
    # Gets the valid start and end dates ——— note df is already sorted
    def ensureDateRange(self, local_df: pd.DataFrame) -> tuple:
        if self.is_df_empty(local_df):
            return (self.fromDate, self.toDate) # no change to dates

        sorted_df = self.sortDataFrame(local_df)
        self.fromDate = sorted_df["Date"].iloc[0]
        self.toDate = sorted_df["Date"].iloc[-1]
        convertedFromDate = self.convert_dateTime_to_QDate(self.fromDate)
        convertedToDate = self.convert_dateTime_to_QDate(self.toDate)

        UIFunctions.setFromDate_max(self, convertedToDate)
        UIFunctions.setToDate_min(self, convertedFromDate)
        return (convertedFromDate, convertedToDate)

    # Gets the current date and creates a new QDate object with it
    def convert_dateTime_to_QDate(self, date) -> QDate:
        return QDate(date.year, date.month, date.day)

    # Loads name from database and calls ui function to add them to the ui
    def loadName(self):
        name = db.getName_from_db()
        name = ["".join(x) for x in name] # handle tuple from db
        if name:
            UIFunctions.addName_to_ui(self,name[0])

    # Changes the name if exists to a new name. Updates database and corresponding ui
    def addName(self, name: str):
        UIFunctions.addName_to_ui(self, name)
        db.addName_to_db(name)

    # Loads accounts from database and calls ui function to add them to the ui
    def loadAccounts(self):
        self.accounts = db.getAccounts_from_db()
        self.accounts = ["".join(x) for x in self.accounts] # handle tuple from db
        if self.accounts:
            UIFunctions.addAllAccounts_to_ui(self, self.accounts)

    # Adds a new account in respective locations
    def addAccount(self, accName: str):
        if accName in self.accounts:
            print("That account already exists!")
            return
        
        self.accounts.append(accName)
        UIFunctions.addAccount_to_ui(self, accName)
        db.addAccount_to_db(accName)
    
    # Updates an exisiting accounts name in all respective locations
    def updateAccount(self, oldAccName: str, newAccName: str):
        if not self.is_df_empty(self.df):
            self.df["Account"].replace(oldAccName, newAccName, inplace=True) #update df
        
        self.accounts[self.accounts.index(oldAccName)] = newAccName # update list
        
        # Clears combo boxes then re-adds them with the updated names
        UIFunctions.clearAllAccountComboBoxes(self)
        UIFunctions.addAllAccounts_to_ui(self, self.accounts)

        UIFunctions.accountsChanged(self, oldAccName, newAccName) # update dashboard
        db.editAccount_in_db(oldAccName, newAccName) # update database

    # Deletes an existing account
    def deleteAccount(self, acc):
        self.accounts.remove(acc)

        if not self.is_df_empty(self.df):
            self.df["Account"].replace(acc, "None", inplace=True) #update df

        UIFunctions.clearAllAccountComboBoxes(self)
        UIFunctions.addAllAccounts_to_ui(self, self.accounts)

        UIFunctions.accountsChanged(self, acc, "None")
        db.editAccount_in_db(acc, "None")

    # Loads transactions from database and sorts it in default reverse chrono order. Returns loaded df
    def loadTransactions(self):
        prev_transactions = db.getTransactions_from_db()

        if not prev_transactions.empty:
            loaded_df = self.sortDataFrame(prev_transactions)
            return loaded_df
        else:
            return pd.DataFrame()

    # Shortcut function to read in multiple csv files at once
    # User must use command "Everything from <directory>" Ex: "Everything from transactions" and select an account
    # CSV files must be named starting with the account name
    def grabMultipleCSV(self, directory: str):
        import os
        currentAccount = UIFunctions.transactionsPage_getAccount_add(self)
        if currentAccount == "Select Account":
            print("You must select an account for this shortcut to work")
            return
        if directory not in os.listdir():
            print("Not a valid directory")
            return

        files = [f for f in os.listdir(directory) if f.endswith('.csv') and f.startswith(currentAccount)]
        for f in files:
            self.readCSVFile(directory + "/" + f)

    # Reads in a csv file and concatenates it with existing transactions dataframe
    # NOTE CSV file must have the DATE column come before MERCHANT, which comes before AMOUNT. Currently only excess columns are "Reference Number", "Address", "Running Bal."
    # TODO improve csv file cleaning + reading only useful columns
    def readCSVFile(self, fileName: str): 
        fileName = fileName.strip()
        if not fileName.endswith(".csv"):
            print("Please enter a csv file")

        try:
            newTransactions_df : pd.DataFrame = pd.read_csv(fileName, usecols=lambda column: column not in ["Reference Number", "Address", "Running Bal.", "Running Balance"])
            newTransactions_df.columns = ["Date", "Merchant", "Amount"] # Rename columns
            
            # Gets currently selected account
            currentAccount = UIFunctions.transactionsPage_getAccount_add(self)
            currentAccount = currentAccount if currentAccount != "Select Account" else "None"
            accountCol = [currentAccount] * newTransactions_df.shape[0]

            categoryCol = ["Restaurants & Dining"] * newTransactions_df.shape[0]

            # Insert account and category columns
            newTransactions_df.insert(2, column="Account", value=accountCol)
            newTransactions_df.insert(3, column="Category", value=categoryCol)
            
            # Converts the date column to datetime object for easy sorting
            newTransactions_df["Date"] = pd.to_datetime(newTransactions_df["Date"], format="%m/%d/%Y")

            # Adds the newly added transactions into the database
            db.addTransactions_to_db(newTransactions_df)

            # combine total transactions with new transactions and remove duplicates if necessary
            self.df = pd.concat([self.df, newTransactions_df]).drop_duplicates().reset_index(drop=True)
            self.ensureDateRange(self.sortDataFrame(self.df)) # sort by asending chronological order
            filtered_df = self.filterDataFrame()
            sorted_df = self.sortDataFrame(filtered_df)
            self.displayed_df = sorted_df
            self.fillTable(sorted_df)

            self.updateDashboard()
            self.updateAnalysisPage()
        except FileNotFoundError:
            print("File ERROR. Please make sure that the specified path and file name is correct")

    # Gets the currently applied filters and filters the dataframe
    def filterDataFrame(self):
        filteredKind = UIFunctions.getKind_filter(self)
        filteredAcc = UIFunctions.getAccount_filter(self)
        filteredCategory = UIFunctions.getCategory_filter(self)
        filteredFromDate: QDate = UIFunctions.getFromDate_filter(self)
        filteredToDate: QDate = UIFunctions.getToDate_filter(self)

        if self.is_df_empty(self.df): return

        df_to_filter = self.df

        # Filter by income or spending
        if filteredKind == "Income from":
            df_to_filter = df_to_filter.loc[df_to_filter['Amount'] > 0]
        elif filteredKind == "Spending from":
            df_to_filter = df_to_filter.loc[df_to_filter['Amount'] < 0]

        # Filter account
        if filteredAcc != "All Accounts":
            df_to_filter = df_to_filter.loc[df_to_filter['Account'] == filteredAcc]

        # Filter category
        if filteredCategory != "All Categories":
            df_to_filter = df_to_filter.loc[df_to_filter['Category'] == filteredCategory]

        # Filter by dates —— must convert QDate objects to datetime
        fromDate_datetime = datetime.combine(filteredFromDate.toPyDate(), datetime.min.time())
        toDate_datetime = datetime.combine(filteredToDate.toPyDate(), datetime.min.time())
        df_to_filter = df_to_filter.loc[(df_to_filter['Date'] >= fromDate_datetime) & (df_to_filter['Date'] <= toDate_datetime)]

        # Update date boundaries so user can't make the to date less than the from date and vice versa 
        UIFunctions.setFromDate_max(self, filteredToDate)
        UIFunctions.setToDate_min(self, filteredFromDate)

        # Sorts the filtered dataframe and displays it
        sorted_df = self.sortDataFrame(df_to_filter)
        self.displayed_df = sorted_df
        UIFunctions.clearTable(self)
        self.fillTable(sorted_df)

        return self.df
    
    # Sorts the dataframe of transactions so the table is ready to be filled
    def sortDataFrame(self, toSort: pd.DataFrame):
        sortMethod = self.MAP_TABLE_TO_SORT[self.selectedHeader]
        return toSort.sort_values(by=[sortMethod], ascending=self.header_ascending)

    # Uses dataframe to create neccessary rows and fill in with data
    def fillTable(self, sorted_df: pd.DataFrame):
        df_array = sorted_df.to_numpy() # converts to numpy so easier to iterate

        for i, row in enumerate(df_array):
            for j, value in enumerate(row):
                # create a new row if the 13 default rows have been filled or if was already populated
                if i == self.ui.transactionsTable.rowCount():
                    self.ui.transactionsTable.insertRow(self.ui.transactionsTable.rowCount())
                
                cell = ""
                if j == 0:
                    cell = value.strftime("%m/%d/%Y")
                elif j == 4:
                    cell = self.formatAmount(value)
                else:
                    cell = str(value)

                self.ui.transactionsTable.setItem(i, j, QTableWidgetItem(cell))

                # format $ amount column to the right
                if j == 4:
                    delegate = AlignDelegate(self.ui.transactionsTable)
                    self.ui.transactionsTable.setItemDelegateForColumn(4, delegate)

        UIFunctions.scrollToBottom(self)

    # Formats the amount into "+/-$X"
    def formatAmount(self, amt) -> str:
        formatted = "{:.2f}".format(amt)
        if amt < 0:
            return formatted[0] + "$" + formatted[1:]
        else:
            return "$" + formatted
    
    # Checks whether the specified dataframe is empty
    def is_df_empty(self, local_df: pd.DataFrame):
        return local_df.empty
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    window = MainWindow()
    sys.exit(app.exec_())