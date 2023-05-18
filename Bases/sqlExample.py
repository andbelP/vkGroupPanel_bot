import sqlite3 as sql

class DataBase:
    def __init__(self,name):
        self.connect = sql.connect(f'{name}.db')
        self.cursor = self.connect.cursor()

    def create_table(self,name,columns):
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name}({columns})")
        self.connect.commit()
    def insert_into(self,name,mask,list):
        self.cursor.execute(f"INSERT INTO {name} VALUES({mask});", list)
        self.connect.commit()
    def delete_table(self,name):
        self.cursor.execute(f'DROP TABLE {name}')
        self.connect.commit()
    def request(self, req):
        return self.cursor.execute(req).fetchall()
        self.cursor.commit()
        self.cursor.close()
    def requestWithoutFetch(self, req):
        self.cursor.execute(req)
        self.connect.commit()
        self.connect.close()