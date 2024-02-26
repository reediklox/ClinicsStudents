import sqlite3 as sql
import pandas as pd


class Writer:
    
    def __init__(self, database) -> None:
        self.__conn = sql.connect(database)
        self.cursor = self.__conn.cursor()
    
    
    def isert(self, clinic_name, student1=None, student2=None, student3=None, student4=None, student5=None):
        try:
            self.cursor.execute('''INSERT INTO Students (polyclinic, student1, student2, student3, student4, student5)
                                VALUES ( ?, ?, ?, ?, ?, ?)''', (clinic_name, student1, student2, student3, student4, student5))
            
            self.__conn.commit()
        except Exception as e:
            print(e)
    
    
    def select(self):
        try:
            self.cursor.execute(f'''SELECT * FROM Students''')
        except Exception as e:
            print(e)
            
    
    def convertToExcel(self):
        df = pd.read_sql_query('''SELECT * FROM Students''', self.__conn)
        df.to_excel('Clinics.xlsx', index=False)
    
    
    def __enter__(self):
        try:
            self.cursor.execute('''CREATE TABLE Students 
                        (polyclinic TEXT PRYMARY KEY, student1 TEXT NULL, 
                                                        student2 TEXT NULL, 
                                                        student3 TEXT NULL,
                                                        student4 TEXT NULL,
                                                        student5 TEXT NULL)''')
        except Exception:
            print("База данных уже создана")
        
        return self
    
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__conn.close()