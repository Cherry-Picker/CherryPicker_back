# 필요한 모듈을 불러온다
from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields, reqparse
from db import account, usercard, connection, models, card
import json, hashlib

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app, version='1.0', title='Cherry Picker API', description='체리 피커 프로젝트에서 사용할 REST API 입니다.')
ns  = api.namespace('user', description='회원 관련 REST API')
usercard_ns = api.namespace('usercard', description="유저 카드 정보 REST API")
card_ns = api.namespace('card', description='카드 정보 API')
event_ns = api.namespace('event', description='카드 이벤트')

account_model = api.model('account', {
    'id': fields.String(required=True, description='사용자 ID'),
    'pw': fields.String(required=True, description='사용자 PW'),
    'nickname': fields.String(required=True, description='사용자 닉네임'),
    'tel': fields.String(required = True, description="사용자 휴대폰 번호")
})

login_model = api.model('account_login_info', {
    'id': fields.String(required=True, description="사용자 ID"),
    'pw': fields.String(required=True, description="사용자 PW (해시)"),
})

delete_model = api.model('account_password', {
    'pw': fields.String(required=True, description="사용자 PW")
})

usercard_model = api.model('usercard', {
    'cardname':fields.String(required=True, description="카드 이름"),
    'id':fields.String(required=True, description="사용자 ID"),
})

card_model = api.model('card', {
    'name': fields.String(required=True, description="카드 이름"),
})


# account
@ns.route('/signup')
class SignUPClass(Resource):
    @ns.expect(account_model)
    def post(self):
        """회원가입시 유저정보를 데이터베이스에 저장합니다."""
        con = connection.connect_db()
        user_id = request.json["id"]
        pw = request.json["pw"]
        nickname = request.json["nickname"]
        tel = request.json["tel"]
        result =  account.insert_account(con, user_id, pw, nickname, tel)
        return {
            models.AccountResult.UNSAFE_PASSWORD: (json.dumps({"message": "안전하지 않은 패스워드 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.DUMPLICATED_ID: (json.dumps({"message": "이미 등록된 아이디 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.SQL_INJECTED: (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.AccountResult.SUCCESS: (json.dumps({"message": "회원가입에 성공하였습니다."}, ensure_ascii=False), 200),
        }[result]
        
@ns.route('/login')
class LoginClass(Resource):
    @ns.expect(login_model)
    def post(self):
        """로그인 시 브라우저에 쿠키를 제공합니다."""
        con = connection.connect_db()
        user_id = request.json["id"]
        pw = request.json["pw"] # 해시값으로
        state, user = account.load_account(con, user_id)
        success = user != None and user.id == user_id and user.pw == pw
        if not success:
            return (json.dumps({"message": "비밀번호가 틀렸거나 없는 아이디 입니다."}, ensure_ascii=False), 401)
        res = make_response()
        res.set_data(json.dumps({"message": "로그인에 성공하였습니다."}, ensure_ascii=False))
        res.set_cookie("token", hashlib.sha256((user_id+pw).encode()).hexdigest())
        res.set_cookie("userid", user_id)
        return res

@ns.route('/update')
class UpdateUserClass(Resource):
    @ns.expect(account_model)
    def post(self):
        """회원의 비밀번호와 닉네임을 변경합니다."""
        con = connection.connect_db()
        user_id = request.json["id"]
        pw = request.json["pw"]
        nickname = request.json["nickname"]
        tel = request.json["tel"]
        token = request.cookies.get("token")
        
        result =  account.update_account(con, user_id, pw, nickname, tel, token)

        res = make_response()
        res.set_data(json.dumps({"message": "회원 정보 업데이트에 성공하였습니다."}, ensure_ascii=False))
        res.set_cookie("token", hashlib.sha256((user_id+pw).encode()).hexdigest())

        return {
            models.AccountResult.UNSAFE_PASSWORD: (json.dumps({"message": "안전하지 않은 패스워드 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.DUMPLICATED_ID:  (json.dumps({"message": "이미 등록된 아이디 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.FAIL:            (json.dumps({"message": "잘못된 접근입니다."}, ensure_ascii=False), 401),
            models.AccountResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.AccountResult.SUCCESS:         res
        }[result]

@ns.route('/logout')
class LogoutClass(Resource):
    def post(self):
        """로그아웃 시 쿠키를 제거합니다"""
        res = make_response()
        res.set_cookie("userid", "", expires = 0)
        res.set_cookie("token", "", expires = 0)
        res.set_data(json.dumps({"message": "로그아웃 성공하였습니다."}, ensure_ascii=False))
        return res

@ns.route('/withdraw')
class WithdrawUserClass(Resource):
    @ns.expect(delete_model)
    def delete(self):
        """회원을 제거합니다."""
        token = request.cookies.get("token")
        userid = request.cookies.get("userid")
        pw = request.json["pw"]
        if hashlib.sha256((userid+pw).encode()).hexdigest() != token:
            print("잘못된 접근입니다.")
            return (json.dumps({"message": "잘못된 접근입니다."}, ensure_ascii=False), 401)
        con = connection.connect_db()
        cursor = con.cursor()
        cursor.execute(f"DELETE FROM accounts WHERE id='{userid}'")
        con.commit()
        print('유저가 성공적으로 제거되었습니다.')
        con.close()
        return (json.dumps({"message": "유저가 성공적으로 제거되었습니다."}, ensure_ascii=False), 200)

# usercards

@usercard_ns.route('/insert')
class InsertUserCardClass(Resource):
    @usercard_ns.expect(usercard_model)
    def put(self):
        """유저가 등록한 카드 정보를 데이터베이스에 입력합니다"""
        con = connection.connect_db()
        user_id = request.json["id"]
        cardname = request.json["cardname"]

        result = usercard.insert_usercard(con, cardname, user_id)
        return {
            models.UserCardResult.FAIL:            (json.dumps({"message": "카드가 이미 존재합니다."}, ensure_ascii=False), 401),
            models.UserCardResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.UserCardResult.SUCCESS:         (json.dumps({"message": "카드 등록에 성공하였습니다."}, ensure_ascii=False), 200),
        }[result]

@usercard_ns.route('/delete')
class DeleteUserCardClass(Resource):
    @usercard_ns.expect(usercard_model)
    def delete(self):
        """유저가 등록했던 카드 정보를 삭제"""
        con = connection.connect_db()
        user_id = request.json["id"]
        cardname = request.json["cardname"]

        result = usercard.remove_usercard(con, cardname, user_id)
        return {
            models.UserCardResult.FAIL:            (json.dumps({"message": "카드가 존재하지 않습니다."}, ensure_ascii=False), 401),
            models.UserCardResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.UserCardResult.SUCCESS:         (json.dumps({"message": "카드를 성공적으로 제거하였습니다."}, ensure_ascii=False), 200),
        }[result]

getUserCardModel = reqparse.RequestParser()
getUserCardModel.add_argument("id", type = str, default=None, help="유저 ID")
@usercard_ns.route('/load')
class LoadUserCardClass(Resource):
    @usercard_ns.expect(getUserCardModel)
    def get(self):
        con = connection.connect_db()
        user_id = request.args.get("id")
        state, cards = usercard.load_usercard(con, user_id)

        return {
            models.UserCardResult.FAIL:(json.dumps({"message": "카드가 존재하지 않습니다."}, ensure_ascii=False), 400),
            models.UserCardResult.SQL_INJECTED: (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}), 500),
            models.UserCardResult.SUCCESS:(json.dumps(cards, ensure_ascii = False), 200)
        }[state]

getCardModel = reqparse.RequestParser()
getCardModel.add_argument("name", type = str, default=None, help="카드 이름")
@card_ns.route('/load')
class LoadCardClass(Resource):
    @ns.expect(getCardModel)
    def get(self):
        """특정 카드의 카드정보 조회"""
        con = connection.connect_db()
        name = request.args.get("name")
        state, c = card.load_card(con, name)

        return {
            models.CardResult.FAIL:(json.dumps({"message": "카드가 존재하지 않습니다."}, ensure_ascii=False), 400),
            models.CardResult.SQL_INJECTED: (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}), 500),
            models.CardResult.SUCCESS:(json.dumps(c, ensure_ascii = False), 200)
        }[state]

@card_ns.route('/search')
class SearchCardClass(Resource):
    @ns.expect(getCardModel)
    def get(self):
        """찾고자 하는 카드의 이름과 유사한 이름을 가진 카드 목록들을 조회"""
        con = connection.connect_db()
        name = request.args.get("name")
        cards = card.search_card(con, name)

        cards.index = cards.index.map(str)
        cards.columns = cards.columns.map(str)
        card_json = str(cards.to_dict(orient="records")).replace("'", '"')
        return card_json
    
getCompanyCardModel = reqparse.RequestParser()
getCompanyCardModel.add_argument("company", type = str, default=None, help="회사 이름")
@card_ns.route('/get_cards')
class GetCardsClass(Resource):
    @card_ns.expect(getCompanyCardModel)
    def get(self):
        """해당하는 회사에서 제공하는 카드 목록들을 조회"""
        con = connection.connect_db()
        company = request.args.get("company")
        cards = card.load_company_card(con, company)
        if len(cards) == 0:
            print("회사 이름이 없습니다.")
            return json.dumps({"message": "회사 이름이 없습니다."}, ensure_ascii = False) , 401
        
        return json.dumps(cards, ensure_ascii = False), 200

getCompanyCardModel = reqparse.RequestParser()
getCompanyCardModel.add_argument("name", type = str, default=None, help="카드 이름")
@event_ns.route('/get_events')
class GetCardEventsClass(Resource):
    @event_ns.expect(getCompanyCardModel)
    def post(self):
        """카드 이벤트들을 조회"""
        con = connection.connect_db()
        name = request.args.get("name")
        cursor = con.cursor()

        cursor.execute(f"SELECT * FROM events WHERE name='{name}'")
        rows = cursor.fetchall()

        con.close()
        if len(rows) != 0:
            print("이벤트가 존재하지 않습니다.")
            return json.dumps({"message": "이벤트가 존재하지 않습니다."}, 401)
        return (json.dumps(rows, default=str,ensure_ascii=False), 200)

if __name__ == "__main__":
    app.run(host='0.0.0.0')