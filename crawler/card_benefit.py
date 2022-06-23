import requests, json, os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from pymysql import Connection

def insert_benefits_info(con: Connection, idx: int):
    response = requests.get(f"https://api.card-gorilla.com:8080/v1/cards/{idx}")
    if response.status_code != 200:
        print('api 접근이 잘못되었습니다.')
        return
    
    body = json.loads(response.text)
    describe = body["seo_meta"][1]["content"].replace("'","").replace('"',"")
    name = body["name"]
    
    cursor = con.cursor()
    try:
        cursor.execute(f"INSERT INTO benefits VALUE ('{name}', '{describe}')")
        con.commit()
    except Exception:
        pass