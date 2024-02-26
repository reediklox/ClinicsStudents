import pandas as pd

class Parser:
    def __init__(self, table, header=None, skiprows=None) -> None:
        self.__table = table
        self.__df = pd.read_excel(table, header=header, skiprows=skiprows).dropna()
        
    def __getDF(self):
        return self.__df
    
    dataframe = property(__getDF)
    
    def getDict(self, key:str, value:str):
        if self.__table == 'resources/Foreigners.xlsx':
            return dict(zip(self.__df[key], self.__df[value]))
        elif self.__table == 'resources/Students.xlsx':
            return dict(zip(self.__df[key], self.__df[value]))
        else:
            return dict(zip(self.__df[key], self.__df[value]))
        