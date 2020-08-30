import sqlite3
from sqlite3 import Error

import sys

import pandas as pd

DB_FILE = "financeData.db"

# Creates a connection between the database specified by file
def create_connection(file: str):
    conn = None
    try:
        conn = sqlite3.connect(file)
        return conn
    except Error as e:
        print(e)
        print("ERROR: Could not create a connection to the database")
        sys.exit()

# Function used to initially create the tables in the database
def createTable(conn: sqlite3.Connection, query: str):
    try:
        c = conn.cursor()
        c.execute(query)
    except Error as e:
        print(e)
        sys.exit()

    conn.commit()

# Drops existing tables 
def resetTables(conn: sqlite3.Connection):
    try:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS transactions")
        c.execute("DROP TABLE IF EXISTS accounts")
        c.execute("DROP TABLE IF EXISTS name")
    except Error as e:
        print(e)
        sys.exit()

    conn.commit()
    c.close()

# Retrieves transactions from database, stores it in a dataframe, and returns the dataframe for use in the app
def getTransactions_from_db() -> pd.DataFrame:
    global DB_FILE
    conn = create_connection(DB_FILE)

    df : pd.DataFrame = pd.read_sql_query("SELECT * FROM transactions", conn)
    df.columns = ["Date", "Merchant", "Account", "Category", "Amount", "Running Balance"] # Rename columns as necessary
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d") # convert date column to datetime
    conn.close()

    return df

# Retrieves accounts from database and returns as a list of accounts. Note the list will be a list of tuples
def getAccounts_from_db() -> list:
    global DB_FILE
    conn = create_connection(DB_FILE)

    c = conn.cursor()
    c.execute("SELECT * FROM accounts")
    accounts = c.fetchall()

    c.close()
    conn.close()

    return accounts

# Retrieves name from database and returns it. Note the list will be a list of tuples
def getName_from_db() -> list:
    global DB_FILE
    conn = create_connection(DB_FILE)

    c = conn.cursor()
    c.execute("SELECT * FROM name")
    name = c.fetchall()

    c.close()
    conn.close()

    return name

# Given a new set of transactions, adds them into the database
def addTransactions_to_db(new_transactions: pd.DataFrame):
    global DB_FILE
    conn = create_connection(DB_FILE)
    
    current_df : pd.DataFrame = pd.read_sql_query("SELECT * FROM transactions", conn)
    current_df.columns = ["Date", "Merchant", "Account", "Category", "Amount", "Running Balance"]
    current_df["Date"] = pd.to_datetime(current_df["Date"], format="%Y-%m-%d")
    new_transactions = pd.merge(new_transactions, current_df, indicator=True, how="outer").query('_merge=="left_only"').drop('_merge', axis=1)
    new_transactions.rename(columns={'Running Balance': 'RunningBalance'}, inplace=True) # Rename running balance column to avoid space when storing in database

    if not new_transactions.empty:
        new_transactions.to_sql(name="transactions", con=conn, if_exists="append", index=False)
        print("Transactions were successfully added!")
    else:
        print("No new transactions were added")

    conn.commit()
    conn.close()


# Given a new account, adds it into the database
def addAccount_to_db(acc: str):
    global DB_FILE
    conn = create_connection(DB_FILE)
        
    conn.execute("INSERT INTO accounts VALUES(?)", (acc,))
    conn.commit()
    conn.close()

    print("Account was successfully added!")

# Given the original name of an account and the name to update it with, updates the account name stored in the database
def editAccount_in_db(oldAccName: str, newAccName: str):
    global DB_FILE
    conn = create_connection(DB_FILE)

    # If the new account is none, we know that we must delete the account not update its name
    if newAccName == "None":
        conn.execute('''DELETE FROM accounts WHERE Name = ?''', (oldAccName,))
    else:
        conn.execute('''UPDATE accounts SET Name = ? WHERE Name = ?''', (newAccName, oldAccName))
    conn.execute('''UPDATE transactions SET Account = ? WHERE Account = ?''', (newAccName, oldAccName))
    conn.commit()
    conn.close()

    print("Account was successfully updated")

# Adds a name into the name table in the database
def addName_to_db(name: str):
    global DB_FILE
    conn = create_connection(DB_FILE)

    conn.execute("DELETE FROM name")
    conn.execute("INSERT INTO name VALUES(?)", (name,))
    conn.commit()
    conn.close()

    print("Name was succesfully updated!")

def main():
    global DB_FILE
    

    query_create_transactions_table = """CREATE TABLE IF NOT EXISTS transactions (
        Date text NOT NULL,
        Merchant text NOT NULL,
        Account text,
        Category text,
        Amount integer NOT NULL,
        RunningBalance integer
    );"""

    query_create_accounts_table = """CREATE TABLE IF NOT EXISTS accounts (
        Name NOT NULL
    );"""

    query_create_name_table = """CREATE TABLE IF NOT EXISTS name (name NOT NULL);"""

    conn = create_connection(DB_FILE)

    # Resets tables
    resetTables(conn)

    createTable(conn, query=query_create_transactions_table)
    createTable(conn, query=query_create_accounts_table)
    createTable(conn, query=query_create_name_table)
    conn.close()

if __name__ == "__main__":
    main()