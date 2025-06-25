import sqlite3
from datetime import datetime, timedelta
import random

class Database:
    def __init__(self):
        self.connection = sqlite3.connect('database.db')
        self.cursor = self.connection.cursor()

        #Users
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users(
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            is_admin INTEGER NOT NULL,
            balance REAL NOT NULL)
        ''')


        #User_slot
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS User_slot(
            id INTEGER PRIMARY KEY,
            owner INTEGER,
            status TEXT NOT NULL,
            plan INTEGER NOT NULL,
            creation_date TEXT DEFAULT (datetime('now')),
            next_payment TEXT NOT NULL,
            key TEXT NOT NULL,
            FOREIGN KEY (owner) REFERENCES Users (id) ON DELETE CASCADE
            )
        ''')#status 0-not work 1-work

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Active_invoices(
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            invoice_id INTEGER NOT NULL,
            amount INTEGER NOT NULL
            )
        ''')

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS Tariffs(
            id INTEGER PRIMARY KEY,
            price INTEGER NOT NULL,
            days INTEGER NOT NULL,
            text TEXT NOT NULL,
            next_tariff INTEGER        
            )
        ''')

        self.connection.commit()

    def __del__(self):
        self.connection.close()

    def get_user(self, user_id):
        self.cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()

        return user
    
    def get_or_create(self, user_id, username):
        self.cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
        user = self.cursor.fetchone()

        return user
    

    def add_user(self, username, user_id):
        self.cursor.execute('INSERT INTO Users (username, user_id, is_admin, balance) VALUES (?,?,?,?)', (username, user_id, 0, 0))
        self.connection.commit()

    def update_user_balance(self, user_id, balance):
        self.cursor.execute('UPDATE Users SET balance=? WHERE user_id=?', (balance,user_id,))
        self.connection.commit()

    def raise_user_balance(self, user_id, sum):
        user = self.get_user(user_id=user_id)
        new_user_balance = int(user[4]) + sum

        self.cursor.execute('UPDATE Users SET balance=? WHERE user_id=?', (new_user_balance,user_id,))
        self.connection.commit()

    def get_all_slots(self, user_id):
        self.cursor.execute('SELECT * FROM User_slot WHERE owner=?', (user_id,))
        return self.cursor.fetchall()


#----------Servers--------------------
    def add_server(self, name, location, ip, status, acceptable_conn, cost):
        self.cursor.execute('INSERT INTO Servers (name, location, ip, status, acceptable_conn, cost) VALUES (?,?,?,?,?,?)', (name, location, ip, status, acceptable_conn, cost))
        self.connection.commit()

    def get_server(self, id):
        self.cursor.execute('SELECT * FROM Servers WHERE id=?',(id,))
        return self.cursor.fetchone()
    
    def get_all_servers(self):
        self.cursor.execute('SELECT * FROM Servers')
        return self.cursor.fetchall()
    
    def del_server(self,id):
        self.cursor.execute('DELETE FROM Servers WHERE id=?', (id))
        self.connection.commit()

    def edit_server(self, id, name, location, ip, status, acceptable_conn, cost):
        self.cursor.execute('UPDATE Servers SET name=?, location=?, ip=?, status=?, acceptable_conn=?, cost=? WHERE id=?', (name, location,status, ip, acceptable_conn,cost, id))
        self.connection.commit()

    def get_regions(self):
        self.cursor.execute('SELECT location from Servers WHERE status=1 AND acceptable_conn>=1')
        return self.cursor.fetchall()
    




#-------------------------------------


#------------USER SLOTS-------------

    def add_slot(self, user_id, plan, key, next_payment):
        
        cur_date = datetime.today()

        self.cursor.execute('INSERT INTO User_slot (owner, plan, status, creation_date, next_payment, key) VALUES (?,?,?,?,?,?)', (user_id, plan, 1, cur_date, next_payment, key))
        self.connection.commit()

        self.cursor.execute('SELECT id FROM User_slot WHERE owner=?', (user_id,))
        return self.cursor.fetchone()[0]

    def change_plan_by_user(self, plan_id, user_id):
        self.cursor.execute('UPDATE User_slot SET plan=? WHERE owner=?', (plan_id, user_id))
        self.connection.commit()

    def get_slot(self, user_id):
        self.cursor.execute('SELECT * FROM User_slot WHERE owner=?', (user_id,))
        return self.cursor.fetchone()
    
    def get_slot_byid(self, slot_id):
        self.cursor.execute('SELECT * FROM User_slot WHERE id=?', (slot_id,))
        return self.cursor.fetchone()
    
    def del_slot(self, slot_id):
        self.cursor.execute('DELETE FROM User_slot WHERE id=?', (slot_id,))
        self.connection.commit()

    def unsub_slot(self, slot_id):
        self.cursor.execute('UPDATE User_slot SET status=? WHERE id=?', (2, slot_id))
        self.connection.commit()

    def resub_slot(self, slot_id):
        self.cursor.execute('UPDATE User_slot SET status=? WHERE id=?', (1, slot_id))
        self.connection.commit()

    def unpaid_slot(self, slot_id):
        self.cursor.execute('UPDATE User_slot SET status=? WHERE id=?', (3, slot_id))
        self.connection.commit()

    def paid_slot(self, slot_id):
        self.cursor.execute('UPDATE User_slot SET status=? WHERE id=?', (1, slot_id))
        self.connection.commit()

    def update_slot_payment(self, slot_id, next_payment):
        self.cursor.execute('UPDATE User_slot SET next_payment=? WHERE id=?', (next_payment, slot_id))
        self.connection.commit()



#invoices-----------------------------------

    def add_invoice(self, user_id, invoice_id, amount):
        self.cursor.execute('INSERT INTO Active_invoices (user_id, invoice_id, amount) VALUES (?,?,?)', (user_id, invoice_id, amount))
        self.connection.commit()

    def get_invoices(self):
        self.cursor.execute('SELECT * FROM Active_invoices')
        return self.cursor.fetchall()
    
    def del_invoice(self, invoice_id):
        self.cursor.execute('DELETE FROM Active_invoices WHERE invoice_id=?', (invoice_id,))
        self.connection.commit()

    def add_tariff(self, price, days, text, next_tariff=None):
        self.cursor.execute('INSERT INTO Tariffs (price, days, text, next_tariff) VALUES (?,?,?,?)', (price, days, text, next_tariff))
        self.connection.commit()

    def tariff_by_id(self, id):
        self.cursor.execute('SELECT * FROM Tariffs WHERE id=?', (id,))
        return self.cursor.fetchone()