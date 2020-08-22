from app import *
from ui_functions import *
from datetime import datetime

class AnalysisFunctions(MainWindow):
    def totalSpendingAndIncome(self):
        if self.is_df_Empty(self.df): return

        currentMonth = datetime.today().month
        prevMonth = (currentMonth - 1) if currentMonth != 1 else 12

        # filter transactions by spending vs income and sum for the month
        df_spendingTransactions = self.df.loc[self.df['Amount'] < 0]
        currMonthTrans = df_spendingTransactions.loc[df_spendingTransactions['Date'].dt.month == currentMonth]
        if not self.is_df_Empty(currMonthTrans):
            monthSpending = currMonthTrans['Amount'].sum().astype(float)
        else:
            monthSpending = 0
        
        df_incomeTransactions = self.df.loc[self.df['Amount'] > 0]
        currMonthTrans = df_incomeTransactions.loc[df_incomeTransactions['Date'].dt.month == currentMonth]
        if not self.is_df_Empty(currMonthTrans):
            monthIncome = currMonthTrans['Amount'].sum().astype(float)
        else:
            monthIncome = 0
        
        # calculate spendings + income percentages per month
        spendingPercentage = AnalysisFunctions.getPercentageChanged(self, df_spendingTransactions, monthSpending)
        incomePercentage = AnalysisFunctions.getPercentageChanged(self, df_incomeTransactions, monthIncome)
        
        UIFunctions.updateSpending(self, monthSpending, spendingPercentage)
        UIFunctions.updateIncome(self, monthIncome, incomePercentage)
    
    # Gets the percentage changed between this and last month
    def getPercentageChanged(self, df_spending: pd.DataFrame, currMonthAmt: float):
        currentMonth = datetime.today().month
        prevMonth = (currentMonth - 1) if currentMonth != 1 else 12

        prevMonthTrans = df_spending.loc[df_spending['Date'].dt.month == prevMonth]

        # only sum column if not empty
        prevMonthSpending = 0
        if not self.is_df_Empty(prevMonthTrans):
            prevMonthSpending = prevMonthTrans['Amount'].sum().astype(float)

        if prevMonthSpending == 0:
            return 100
        
        percentage = (currMonthAmt - prevMonthSpending) / prevMonthSpending * 100
        return round(percentage, 2)