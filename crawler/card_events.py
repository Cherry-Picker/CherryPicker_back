import requests, json, re, os, sys
from bs4 import BeautifulSoup
from pymysql import Connection
from datetime import datetime
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

def find_date(date_string: str) -> list[str]:
    dot_splited_pattern = re.compile("\d{2,4}\.\s{0,1}\d{1,2}\.\s{0,1}\d{1,2}")
    dash_splited_pattern = re.compile("\d{2,4}\s{0,1}-\s{0,1}\d{1,2}\s{0,1}-\s{0,1}\d{1,2}")
    slash_splited_pattern = re.compile("\d{2,4}/\s{0,1}\d{1,2}/\s{0,1}\d{1,2}")
    ko_pattern = re.compile("\d{2,4}년{1}\s\d{1,2}월{1}\s{0,1}\d{1,2}일{1}") 
    return [re.compile("\d+").findall(date) for pattern in [dot_splited_pattern,
                                 dash_splited_pattern,
                                 ko_pattern, 
                                 slash_splited_pattern] for date in pattern.findall(date_string)]


def insert_card_events(con: Connection,idx: int):
    response = requests.get(f"https://api.card-gorilla.com:8080/v1/cards/{idx}")
    json_data = json.loads(response.text)
    pr_detail = json_data["pr_detail"]
    if pr_detail == None:
        print("이벤트를 제공하지 않습니다.")
        return
    soup  = BeautifulSoup(pr_detail)
    script_tag = soup.find_all(['script', 'style', 'header', 'footer', 'form'])

    for script in script_tag:
        script.extract()
        
    content = soup.get_text('\n', strip=True)
    dates = find_date(content)
    for index in range(len(dates)):
        try:
            if len(dates[index][0]) != 4:
                dates[index][0] = "20" + dates[index][0]

            if len(dates[index][1]) == 1:
                dates[index][1] = "0" + dates[index][1]

            if len(dates[index][2]) == 1:
                dates[index][2] = "0" + dates[index][2]
            
            dates[index] = "-".join(dates[index])
            dates[index] = datetime.strptime(dates[index], "%Y-%m-%d")

        except:
            pass
    try:
        name = json_data["name"]
        findate = max(dates)
        if findate < datetime.now():
            print("이벤트를 더이상 제공하지 않습니다.")
            return
        description = content.replace('"','').replace("'","")
        
        cursor = con.cursor()
        cursor.execute(f"INSERT INTO events VALUES ('{name}', '{findate}', '{description}');")
        print('데이터 입력 성공')
        con.commit()
    except:
        pass