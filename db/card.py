from db.models import *
from pymysql import Connection
import pandas as pd
from soynlp.hangle import jamo_levenshtein

def load_card(connection: Connection, name: str) -> tuple:
    
    cursor = connection.cursor()
    if ('"' in name or "'" in name):
        print('SQL 문법 오류가 발생하였습니다.')
        return (CardResult.SQL_INJECTED, None)
    cursor.execute(f"SELECT * FROM cards WHERE name='{name}'")
    rows = cursor.fetchall()

    connection.commit()
    if len(rows) == 0:
        print('카드정보가 존재하지 않습니다.')
        return (CardResult.FAIL, None)

    return (CardResult.SUCESS, rows[0])

def search_card(connection: Connection, name: str):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cards")
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns = ["name", "company", "front"])
    df["distance"] = [jamo_levenshtein(dfname, name) for dfname in df.name]
    df = df.sort_values("distance", axis = 0)

    connection.commit()
    return df.head()
    
def insert_card(connection: Connection, name: str, company: str, front: str):
    
    cursor = connection.cursor()
    cursor.execute(f"INSERT INTO cards VALUE ('{name}', '{company}', '{front}');")

    connection.commit()
