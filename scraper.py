import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error
import time

headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134'}

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

database = r"prices.db"

sql_create_prices_table = """CREATE TABLE IF NOT EXISTS prices (
                                    id integer PRIMARY KEY,
                                    URL text NOT NULL,
                                    Title text NOT NULL,
                                    cPrice real
                                );"""

# create a database connection
conn = create_connection(database)

# create table
if conn is not None:
    # create prices table
    create_table(conn, sql_create_prices_table)
    print('Database created')
else:
    print("Error! cannot create the database connection.")

# add item to database
def addItem():
    URL = input('Paste URL: ')
    page = requests.get(URL, headers = headers)

    if page.status_code != 200:
        print('Not able to retrieve page. Try later')
        return

    soup = BeautifulSoup(page.content, 'lxml')        
        
    title = soup.find(id = 'productTitle').get_text().strip()
    price = soup.find(id = 'priceblock_ourprice').get_text()
    price = price[1:]
    price_conv = float(price)
    success = input('Does the price look right (y/n): ' + price + ' ')
    if success == 'n':
        print('Perhaps too many requests. Come back later')
        return
    elif success == 'y':
        print('Adding to database')
    insert_query = '''INSERT INTO prices (URL, Title, cprice)
                      VALUES (?,?,?); '''
    cur = conn.cursor()
    cols = (URL, title, price_conv)
    cur.execute(insert_query, cols)
    conn.commit() 


# delete link from database
def deleteItem():
    ID = input('Delete ID: ')
    ID = int(ID)
    delete_query = 'DELETE FROM prices WHERE id = ?'
    cur = conn.cursor()
    cur.execute(delete_query, (ID,))
    conn.commit()

# checks all items in database to see if price has dropped
def checkPriceChange():
    while True:
        cur = conn.cursor()
        select_query = 'SELECT * FROM prices'
        for row in cur.execute(select_query):
            URL = row[1]
            page = requests.get(URL, headers=headers)
            
            if page.status_code != 200:
                print('checkPriceChange: Not able to retrieve page for item: ', row[0])          
            else:
                soup = BeautifulSoup(page.content, 'lxml')
                price = soup.find(id = 'priceblock_ourprice').get_text()
                price = price[1:]
                price_conv = float(price)

                if price_conv < row[3]:
                    print("Price dropped for item: ", row[0], "!!!")
                    print("Email sending")
                else:
                    print('Price did not drop for item: ', row[0])
            time.sleep(2.0)
        print("Will check for price changes again in 24 hours.")
        time.sleep(24*60*60)   
    

# prints all items in database
def printAllItems():
    cur = conn.cursor()
    cur.execute("SELECT * FROM prices")
 
    rows = cur.fetchall()
 
    for row in rows:
        print(row)

def main():
    print('Welcome to the Scraper. For now this will work for most Amazon products')
    print('Enter number to complete task from menu')
    print('1: Add new item to database')
    print('2: Delete item from database')
    print('3: Print all items in database')
    print('4: Check for price drops. Program will check once every 24 hours.')
    choice = input()
    if choice == '1':
        addItem()
    elif choice == '2':
        deleteItem()
    elif choice == '3':
        printAllItems()
    elif choice == '4':
        checkPriceChange()
    else:
        print('Enter valid number')


if __name__ == '__main__':
    main()


    