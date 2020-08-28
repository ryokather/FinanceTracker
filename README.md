# Finance Tracker

Finance Tracker is a GUI-based desktop application built fully in Python. This application serves as a personal finance management tool that is
able to display, filter, and analyze one's spending and income habits. 

![](demos/demo.gif)

## Prerequisites

-   Python 3.7 or later

## Setup

### Displaying fonts

The font used in this application is Open Sans. Make sure that the font is installed for the application to be correctly displayed.
A link to install the font is found in `assets/fonts`.

### Installing dependencies and setting up virtual environment

To setup a Python virtual environment and install the necessary dependencies, execute the following commands.

```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

You will then need to setup the database that is used with the application. Execute the following command.

`python3 db.py`

## Usage

Once the virtual environment has been activated, run `app.py` to start up Finance Tracker.

As not all bank statements provide the account that the transactions are coming from, it is useful to manually add this to see difference in spending/income per account. To manually label an account to a specific set of transactions, head over to the **Accounts** tab. Now, when you go to add transaction data in the **Transactions** tab you are now able to select which account the transactions are coming from from the drop down menu.

![](demos/demoAddAcc.gif)

There are two methods of adding transactions into the applications

1.  In the  `Enter name and path to csv file` line, enter the path to and name of the csv file. If an account is not selected from the account select
    dropdown menu, the account will be defaulted to None.

![](demos/demoAdd.gif)

2.  Since adding one CSV file at a time can be cumbersome, you are able to batch add CSV files from a specific account. To use this approach, 
    the following steps must be followed accurately:
    1.  Select an account from the dropdown menu.
    2.  Make sure that the transactions to add all begin with the name of the account and ends with the file extension `.csv` 
    3.  In the  `Enter name and path to csv file` line, enter `Everything from directoryName` where directoryName corresponding to the directory in which
        your transactions reside.

![](demos/demoBatchAdd.gif)

You also are able to filter the displayed transactions in any way including filtering by income vs spending, categories, accounts, and date ranges.
Additionally, if you click on the headers of the table you are able to sort by the respective column.

![](demos/demoFilter.gif)

Viewing the **Analysis** tab will provide useful insight into one's spending and income trends.

![](demos/demoAnalysis.gif)

## Built With

-   PyQt5 - A Python version of Qt designed as a cross-platform GUI framework
-   QtCreator - A cross-platform application that uses the Qt API and simplifies the design process of ui

## Project Status

-   Currently, the dashboard is unable to determine the current balance of each account as the application requires any row detailing excess information 
    such as running, starting, or ending balance to be removed. Improvements will be made to improve file reading. For now please make sure that csv files
    are formatted similar to the files in `sampleTransactions`

-   Currently, the application requires the columns representing Date, Merchant/Description, and Amount to explicitly come in that order for the program to
    work. Additionally, columns titled "Reference Number", "Address", and "Running Bal."/"Running Balance" are filtered out. The filtered out columns were
    determined according to Bank of America statements but they may or may not be different from another bank. Improvements are being made to handle csv
    files with a wider range of columns.

-   Category recognition of transactions is planned for the future.

## Issues

-   Credit card payments are being counted as spending and the equivalent payment on a credit card statement is being counted as spending. This flaws
    the calculation of income and essentially double counts one's spendings.

