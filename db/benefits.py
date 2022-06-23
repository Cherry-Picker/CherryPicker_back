from db.models import *
from pymysql import Connection

def load_benefits(connection: Connection, name:str) -> tuple:
    cursor = connection.cursor()
    if ('"' in name) or ("'" in name):
        print('SQL 문법 오류가 발생하였습니다.')
        return (BenefitResult.SQL_INJECTED, None)
    cursor.execute(f"SELECT * FROM benefits WHERE name='{name}'")
    rows = cursor.fetchall()

    if len(rows) == 0:
        print('카드가 등록되어 있지 않습니다.')
        return (BenefitResult.FAIL, None)

    return (BenefitResult.SUCCESS, rows)
