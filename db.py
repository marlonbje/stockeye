import sqlite3
import pandas as pd
import logging

class Database:
    def __init__(self, clientId: str) -> None:
        self.clientId = clientId
        self.logger = logging.getLogger(__class__.__name__)
        self.con = sqlite3.connect(f"{clientId}.db", check_same_thread=False)
        self.cur = self.con.cursor()
        
    def __repr__(self) -> str:
        return f"Database({self.clientId})"
        
    def getTableNames(self) -> list:
        self.cur.execute("SELECT NAME FROM sqlite_master WHERE TYPE='table'")
        names = [name[0] for name in self.cur.fetchall()]
        return names
    
    def addTable(self, tableName: str, data: pd.DataFrame) -> None:
        try:
            data.index.name = "index"
            data.to_sql(name=tableName, con=self.con, if_exists="append")
            self.con.commit()
        except Exception as e:
            self.logger.error(f"{self} | Failed adding {tableName}: {e}")
        
    def getTable(self, tableName: str) -> pd.DataFrame:
        names = self.getTableNames()
        if tableName in names:
            data = pd.read_sql(f"SELECT * FROM {tableName}", con=self.con, index_col="index", parse_dates=True)
            return data
        else:
            self.logger.error(f"{self} | {tableName} not found")
            return pd.DataFrame()
        
    def close(self) -> None:
        self.con.close()
