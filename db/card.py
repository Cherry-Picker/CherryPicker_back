from db.models import *
from pymysql import Connection

def is_exist_card(connection: Connection, card_name: str, user_id: str) -> bool:
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM usercards WHERE id='{user_id}' AND name='{card_name}'")
    rows = cursor.fetchall()
    return len(rows) != 0
    
    
def insert_card(connection: Connection, card_name: str, user_id: str) -> CardResult:
    cursor = connection.cursor()
    if '"' in user_id+card_name :
        print('SQL 문법 오류가 발생하였습니다.')
        return CardResult.SQL_INJECTED
    
    if is_exist_card(connection, card_name, user_id):
        print('해당 유저의 카드는 이미 등록되어 있습니다.')
        return CardResult.FAIL
    
    cursor.execute(f"INSERT INTO usercards(id, name) VALUES ('{user_id}', '{card_name}')")
    print('usercards에 정보가 추가되었습니다.')
    connection.commit()
    connection.close()

    return CardResult.SUCCESS

def remove_card(connection: Connection, card_name:str, user_id:str) -> CardResult:
    cursor = connection.cursor()
    if '"' in user_id+card_name :
        print('SQL 문법 오류가 발생하였습니다.')
        return CardResult.SQL_INJECTED
        
    if not is_exist_card(connection, card_name, user_id):
        print('카드가 존재하지 않습니다.')
        return CardResult.FAIL
    
    cursor.execute(f"DELETE * FROM usercards WHERE id='{user_id}' AND name='{card_name}'")
    print('카드가 성공적으로 제거되었습니다.')
    connection.commit()
    connection.close()
    return CardResult.SUCCESS

   