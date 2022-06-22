import hashlib
from db.models import *
from pymysql import Connection


def load_account(connection: Connection, user_id: str) -> Account:
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM accounts WHERE id='{user_id}'")
    rows = cursor.fetchall()
    if len(rows) == 0:
        print('유저 정보가 존재하지 않습니다.')
        return None
    account = Account(*rows[0])
    print('유저 정보를 성공적으로 불러왔습니다.')

    connection.close()
    return account
    

def insert_account(connection: Connection, user_id: str, user_pw: str, user_nickname: str, user_tel:str) -> AccountResult:
    cursor = connection.cursor()
    if '"' in user_id+user_pw+user_nickname+user_tel:
        print('SQL 문법 오류가 발생하였습니다.')
        return AccountResult.SQL_INJECTED
    
    if len(user_pw) < 8:
        print('비밀번호가 너무 짧습니다.')
        return AccountResult.UNSAFE_PASSWORD

    if load_account(connection, user_id) != None:
        print('아이디가 이미 존재합니다.')
        return AccountResult.DUMPLICATED_ID

    insert_pw = hashlib.sha256(user_pw.encode()).hexdigest()

    cursor.execute(f"INSERT INTO accounts VALUE ('{user_id}','{insert_pw}','{user_nickname}', '{user_tel}')")
    connection.commit()
    print('유저 정보 입력에 성공했습니다.')
    connection.close()
    return AccountResult.SUCCESS


def update_account(connection: Connection, user_id: str, new_pw: str, new_nickname: str, new_tel:str):
    user = load_account(connection, user_id)
    
    if user == None:
        print('유저가 존재하지 않습니다.')
        return AccountResult.NO_ID
    
    if new_pw == None:
        new_pw = user.pw

    if new_nickname == None:
        new_nickname = user.nickname

    if new_tel == None:
        new_tel = user.tel
    
    if '"' in user_id+new_pw+new_nickname+new_tel:
        print('SQL 문법 오류가 발생하였습니다.')
        return AccountResult.SQL_INJECTED

    cursor = connection.cursor()
    cursor.execute(f"UPDATE accounts SET pw='{new_pw}' && nickname='{new_nickname}' && tel='{new_tel}' WHERE id='{id}'")
    connection.commit()
    print('유저 정보 업데이트를 완료했습니다.')

    connection.close()
    return AccountResult.SUCCESS

