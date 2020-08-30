from app import *
from ui_functions import *
from datetime import datetime

class AnalysisFunctions(MainWindow):
    MONTH_TO_NUMBER = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12}
    
    ### DASHBOARD FUNCTIONS ###

    # gets the balance of a specified account
    def getAccountBalance(self, acc: str) -> float:
        accountTransactions = self.df.loc[self.df['Account'] == acc]
        if self.is_df_empty(accountTransactions): return -1
        accountTransactions = accountTransactions.sort_values(by=['Date'], ascending=True)
        return accountTransactions['Running Balance'].iloc[-1].astype(float)

    # Updates the dashboard's current month spending + income as well as the percentage changed
    def updateTotalSpendingAndIncome(self):
        if self.is_df_empty(self.df): return

        currentMonth = datetime.today().month

        # filter transactions by spending vs income and sum for the month
        df_spendingTransactions = self.df.loc[self.df['Amount'] < 0]
        currMonthTrans = df_spendingTransactions.loc[df_spendingTransactions['Date'].dt.month == currentMonth]
        currMonthTrans = AnalysisFunctions.filterOutBillPayments(self, currMonthTrans)
        if not self.is_df_empty(currMonthTrans):
            monthSpending = currMonthTrans['Amount'].sum().astype(float)
        else:
            monthSpending = 0
        
        df_incomeTransactions = self.df.loc[self.df['Amount'] > 0]
        currMonthTrans = df_incomeTransactions.loc[df_incomeTransactions['Date'].dt.month == currentMonth]
        currMonthTrans = AnalysisFunctions.filterOutBillPayments(self, currMonthTrans)
        if not self.is_df_empty(currMonthTrans):
            monthIncome = currMonthTrans['Amount'].sum().astype(float)
        else:
            monthIncome = 0
        
        # calculate spendings + income percentages per month
        spendingPercentage = AnalysisFunctions.getPercentageChanged(self, df_spendingTransactions, monthSpending)
        incomePercentage = AnalysisFunctions.getPercentageChanged(self, df_incomeTransactions, monthIncome)
        
        UIFunctions.updateSpending(self, monthSpending, spendingPercentage)
        UIFunctions.updateIncome(self, monthIncome, incomePercentage)
    
    # Gets the percentage changed between this and last month's spending or income
    def getPercentageChanged(self, df_spending: pd.DataFrame, currMonthAmt: float):
        currentMonth = datetime.today().month
        prevMonth = (currentMonth - 1) if currentMonth != 1 else 12

        prevMonthTrans = df_spending.loc[df_spending['Date'].dt.month == prevMonth]
        prevMonthTrans = AnalysisFunctions.filterOutBillPayments(self, prevMonthTrans)

        # only sum column if not empty
        prevMonthSpending = 0
        if not self.is_df_empty(prevMonthTrans):
            prevMonthSpending = prevMonthTrans['Amount'].sum().astype(float)

        if prevMonthSpending == 0:
            return 100
        
        percentage = (currMonthAmt - prevMonthSpending) / prevMonthSpending * 100
        return round(percentage, 2)
    
    ### ANALYSIS PAGE FUNCTIONS

    # Driver function that updates all the analysis tabs. Called when new transactions are added
    def updateTabs(self):
        index = UIFunctions.analysisPage_spending_getRange(self)
        spending_numMonths = self.INDEX_TO_MONTHRANGE[index]
        AnalysisFunctions.updateSpendingTab(self, spending_numMonths)

        index = UIFunctions.analysisPage_income_getRange(self)
        income_numMonths = self.INDEX_TO_MONTHRANGE[index]
        AnalysisFunctions.updateIncomeTab(self, income_numMonths)
    
    # Updates the spending tab's graph and average spending
    def updateSpendingTab(self, numMonths : int):
        self.ui.widget_spendingPlot.canvas.ax.cla() # clears current axes/plot so can be redrawn
        spendingData = AnalysisFunctions.getSpendingGraphData(self, numMonths)
        AnalysisFunctions.plotSpending(self, spendingData, numMonths)
        avgSpending = AnalysisFunctions.getAverageSpending(self, numMonths)
        UIFunctions.analysisPage_updateAvgSpending(self, avgSpending)

    # Updates the income tab's graph and average income
    def updateIncomeTab(self, numMonths : int):
        self.ui.widget_incomePlot.canvas.ax.cla() # clears current axes/plot so can be redrawn
        incomeData = AnalysisFunctions.getIncomeGraphData(self, numMonths)
        AnalysisFunctions.plotIncome(self, incomeData, numMonths)
        avgIncome = AnalysisFunctions.getAverageIncome(self, numMonths)
        UIFunctions.analysisPage_updateAvgIncome(self, avgIncome)

    # Gets the data to display for the income bar chart
    def getIncomeGraphData(self, numMonths: int):
        NUMBER_TO_MONTH = {1: "Jan", 2: "Feb", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12:"Dec"}

        # if our transactions table is empty income will be 0 for the last 6 months
        if self.is_df_empty(self.df):
            toReturn = [x[1:] for x in AnalysisFunctions.generateZeroMonths(self, numMonths)]
            return pd.DataFrame(toReturn[::-1], columns=['date', 'income'])
        
        # Filter by income and then group together transactions of the same month
        df_incomeTransactions = self.df.loc[self.df['Amount'] > 0]
        df_incomeTransactions = AnalysisFunctions.filterOutBillPayments(self, df_incomeTransactions)
        incomeGrouped = df_incomeTransactions['Amount'].groupby([(df_incomeTransactions.Date.dt.year.rename('year')),
                (df_incomeTransactions.Date.dt.month.rename('month'))]).sum().to_frame(name = 'income').reset_index()

        # Fill in missing months as needed and update the names of the columns
        incomeGrouped = AnalysisFunctions.fillMissingMonthsInDF(self, incomeGrouped, numMonths)
        incomeGrouped['month'] = incomeGrouped['month'].apply(lambda x: NUMBER_TO_MONTH[x]) # apply the name of the actual month
        incomeGrouped['date'] = incomeGrouped['month'].astype(str) + " " + incomeGrouped['year'].astype(str) # combine the month and year

        # Delete excess columns from dataframe
        del incomeGrouped['month']
        del incomeGrouped['year']

        columnHeaders = ['date', 'income']
        incomeGrouped = incomeGrouped.reindex(columns=columnHeaders)
        return incomeGrouped.tail(numMonths)
    
    # Plots the income bar chart
    def plotIncome(self, data: pd.DataFrame, numMonths: int):
        data.reset_index(drop=True, inplace=True)
        ax = data.plot(x='date', y='income', rot=0, kind='bar', ax=self.ui.widget_incomePlot.canvas.ax, legend=None)

        ax.set_xlabel('Month', fontname="Open Sans",fontsize=14)
        ax.set_ylabel('Income', fontname="Open Sans",fontsize=14)
        title = ("Past " + str(numMonths) + " Months Income") if numMonths == 6 or numMonths == 3 else "Income in Past Year" 
        ax.set_title(title, fontname="Open Sans", fontsize=18, color="#4f4f4f")
        ax.spines['bottom'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['top'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['right'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['left'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.xaxis.label.set_color('#4f4f4f')
        ax.yaxis.label.set_color('#4f4f4f')

        ax.tick_params(axis='x', colors=(0.079, 0.079, 0.079, 0.75))
        ax.tick_params(axis='y', colors=(0.079, 0.079, 0.079, 0.75))

        for tick in ax.get_xticklabels():
            tick.set_fontname("Open Sans")
            tick.set_fontsize('8')
        for tick in ax.get_yticklabels():
            tick.set_fontname("Open Sans")
            tick.set_fontsize('8')

        self.ui.widget_incomePlot.canvas.draw()
        
    # Gets the income from a specified month
    def getIncomeInMonth(self, month: str) -> float:
        if self.is_df_empty(self.df): return 0

        monthNum = AnalysisFunctions.MONTH_TO_NUMBER[month] # Must convert the string to the corresponding number        
        df_incomeTransactions = self.df.loc[self.df['Amount'] > 0]
        df_transInMonth = df_incomeTransactions.loc[df_incomeTransactions['Date'].dt.month == monthNum]
        df_transInMonth = AnalysisFunctions.filterOutBillPayments(self, df_transInMonth)
        if self.is_df_empty(df_transInMonth):
            return 0
        return df_transInMonth['Amount'].sum().astype(float) 

    # Gets the average earned income in the past "numMonths" rounded to two decimals
    def getAverageIncome(self, numMonths: int) -> float:
        if self.is_df_empty(self.df):
            return 0.00
        
        df_incomeTransactions = self.df.loc[self.df['Amount'] > 0]
        df_incomeTransactions = AnalysisFunctions.filterOutBillPayments(self, df_incomeTransactions)
        incomeGrouped = df_incomeTransactions['Amount'].groupby([(df_incomeTransactions.Date.dt.year.rename('year')),
                (df_incomeTransactions.Date.dt.month.rename('month'))]).sum().to_frame(name = 'income').reset_index()
        incomeGrouped = AnalysisFunctions.fillMissingMonthsInDF(self, incomeGrouped, numMonths) # fill missing months if necessary
        incomeGrouped = incomeGrouped.tail(numMonths)
        return round(incomeGrouped['income'].mean(), 2)

    # Gets the data to display for the spending bar chart
    def getSpendingGraphData(self, numMonths: int):
        NUMBER_TO_MONTH = {1: "Jan", 2: "Feb", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12:"Dec"}

        # if our transactions table is empty income will be 0 for the last 6 months
        if self.is_df_empty(self.df):
            toReturn = [x[1:] for x in AnalysisFunctions.generateZeroMonths(self, numMonths)]
            return pd.DataFrame(toReturn[::-1], columns=['date', 'spending'])
        
        # Filter by spending, filter out payments, and then group together transactions of the same month
        df_spendingTransactions = self.df.loc[self.df['Amount'] < 0]
        df_spendingTransactions = AnalysisFunctions.filterOutBillPayments(self, df_spendingTransactions)
        spendingGrouped = df_spendingTransactions['Amount'].groupby([(df_spendingTransactions.Date.dt.year.rename('year')),
                (df_spendingTransactions.Date.dt.month.rename('month'))]).sum().to_frame(name = 'spending').reset_index()

        # Fill in missing months as needed and update the names of the columns
        spendingGrouped = AnalysisFunctions.fillMissingMonthsInDF(self, spendingGrouped, numMonths)
        spendingGrouped['month'] = spendingGrouped['month'].apply(lambda x: NUMBER_TO_MONTH[x]) # apply the name of the actual month
        spendingGrouped['date'] = spendingGrouped['month'].astype(str) + " " + spendingGrouped['year'].astype(str) # combine the month and year
        
        # Delete excess columns from dataframe
        del spendingGrouped['month']
        del spendingGrouped['year']

        columnHeaders = ['date', 'spending']
        spendingGrouped = spendingGrouped.reindex(columns=columnHeaders)
        spendingGrouped['spending'] = spendingGrouped['spending'] * -1 # multiply column by -1 so spending becomes positive
        return spendingGrouped.tail(numMonths)

    # Plots the spending bar chart
    def plotSpending(self, data: pd.DataFrame, numMonths: int):
        data.reset_index(drop=True, inplace=True)
        ax = data.plot(x='date', y='spending', rot=0, kind='bar', ax=self.ui.widget_spendingPlot.canvas.ax, legend=None)

        ax.set_xlabel('Month', fontname="Open Sans",fontsize=14)
        ax.set_ylabel('Spending', fontname="Open Sans",fontsize=14)
        title = ("Past " + str(numMonths) + " Months Spending") if numMonths == 6 or numMonths == 3 else "Spending in the Past Year" 
        ax.set_title(title, fontname="Open Sans", fontsize=18, color="#4f4f4f")
        ax.spines['bottom'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['top'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['right'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.spines['left'].set_color((0.079, 0.079, 0.079, 0.25))
        ax.xaxis.label.set_color('#4f4f4f')
        ax.yaxis.label.set_color('#4f4f4f')

        ax.tick_params(axis='x', colors=(0.079, 0.079, 0.079, 0.75))
        ax.tick_params(axis='y', colors=(0.079, 0.079, 0.079, 0.75))

        for tick in ax.get_xticklabels():
            tick.set_fontname("Open Sans")
            tick.set_fontsize('8')
        for tick in ax.get_yticklabels():
            tick.set_fontname("Open Sans")
            tick.set_fontsize('8')

        self.ui.widget_spendingPlot.canvas.draw()
    
    # Gets the amount spent in a specified month
    def getSpendingInMonth(self, month: str) -> float:
        if self.is_df_empty(self.df): return 0

        monthNum = AnalysisFunctions.MONTH_TO_NUMBER[month] # Must convert the string to the corresponding number
        df_spendingTransactions = self.df.loc[self.df['Amount'] < 0]
        df_transInMonth = df_spendingTransactions.loc[df_spendingTransactions['Date'].dt.month == monthNum]
        df_transInMonth = AnalysisFunctions.filterOutBillPayments(self, df_transInMonth)
        if self.is_df_empty(df_transInMonth):
            return 0
        return abs(df_transInMonth['Amount'].sum().astype(float)) 
    
    # Gets the average money spent in the past "numMonths" and rounds it to 2 decimals
    def getAverageSpending(self, numMonths: int) -> float:
        if self.is_df_empty(self.df):
            return 0.00
            
        df_spendingTransactions = self.df.loc[self.df['Amount'] < 0]
        df_spendingTransactions = AnalysisFunctions.filterOutBillPayments(self, df_spendingTransactions)
        spendingGrouped = df_spendingTransactions['Amount'].groupby([(df_spendingTransactions.Date.dt.year.rename('year')),
                (df_spendingTransactions.Date.dt.month.rename('month'))]).sum().to_frame(name = 'spending').reset_index()
        spendingGrouped = AnalysisFunctions.fillMissingMonthsInDF(self, spendingGrouped, numMonths) # fill missing months if necessary
        spendingGrouped = spendingGrouped.tail(numMonths)
        return abs(round(spendingGrouped['spending'].mean(), 2))
    
    ### HELPER FUNCTIONS ###

    # Function that filters out bill payments from a dataframe of transactions
    # NOTE If a transactions has the word "payment" in it, it will get filtered out --> have not seen any transactions with "payment" in it
    def filterOutBillPayments(self, toFilter: pd.DataFrame):
        if self.is_df_empty(toFilter): return toFilter
        return toFilter[~toFilter['Merchant'].str.contains("payment", case=False)]

    # Helper functions to fill in missing data. For example, if in may and june there was no income/spending, we would want to explicitly
    # note this as $0 because the original dataframe would not even have those rows 
    def generateZeroMonths(self, numMonths: int) -> list:
        month, year = datetime.today().month, datetime.today().year
        missingRows = []
        for _ in range(numMonths):
            missingRows.append([year, month, 0])
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        return missingRows
    
    # NOTE probably not the best implementation
    # Fills in a dataframe's missing month rows
    def fillMissingMonthsInDF(self, toFill: pd.DataFrame, numMonths: int) -> pd.DataFrame:
        missingRows = AnalysisFunctions.generateZeroMonths(self, numMonths)

        # Find rows (months) that are missing
        for row in toFill.tail(numMonths)[::-1].itertuples():
            for sub_list in missingRows:
                if row.month == sub_list[1] and row.year == sub_list[0]:
                    missingRows.remove(sub_list)
                    break
        
        toFill = toFill.append(pd.DataFrame(missingRows, columns=toFill.columns), ignore_index=True) # add the missing rows to the dataframe
        toFill.sort_values(by=['year','month'], ascending=[True, True], inplace=True) # sort by correct order
        return toFill