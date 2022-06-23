import requests, json, os, sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from db.card import insert_card
from pymysql import Connection
from db.connection import connect_db

corp_number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 14, 15, 19, 20, 21, 22, 23, 24, 25, 27, 28, 29, 30, 32, 47]
cards = []

def insert_card_info(con: Connection):
    for corp_number in corp_number_list:
        response = requests.get(f"https://api.card-gorilla.com:8080/v1/cards/search?p=1&perPage=10000&corp={corp_number}")
        if response.status_code != 200:
            print('api 접근이 잘못되었습니다.')
            return []
        datas = json.loads(response.text)["data"]
        for data in datas:
            cards.append({
                "name": data["name"],
                "corp": data["corp_txt"],
                "img_url": data["card_img"]["url"],
                "idx": data["idx"]
            })

    for c in cards:
        try:
            insert_card(con, c["name"], c["corp"], c["img_url"])
            pass
        except:
            pass

        yield int(c["idx"])

