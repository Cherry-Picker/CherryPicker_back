# 필요한 모듈을 불러온다
from flask import Flask, request, make_response
from flask_restx import Api, Resource, fields
from db import account, usercard, connection, models
import json, hashlib

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
api = Api(app, version='1.0', title='Cherry Picker API', description='체리 피커 프로젝트에서 사용할 REST API 입니다.')
ns  = api.namespace('user', description='회원 관련 REST API')
usercard_ns = api.namespace('usercard', description="카드 관련 REST API")


account_model = api.model('account', {
    'id': fields.String(required=True, description='사용자 ID'),
    'pw': fields.String(required=True, description='사용자 PW'),
    'nickname': fields.String(required=True, description='사용자 닉네임'),
    'tel': fields.String(required = True, description="사용자 휴대폰 번호")
})

login_model = api.model('login_account', {
    'id': fields.String(required=True, description="사용자 ID"),
    'pw': fields.String(required=True, description="사용자 PW (해시)"),
})

delete_model = api.model('password_account', {
    'pw': fields.String(required=True, description="사용자 PW")
})

usercard_model = api.model('usercard_model', {
    'cardname':fields.String(required=True, description="카드 이름"),
    'id':fields.String(required=True, description="사용자 ID"),
})

card_model = api.model('card_model', {
    'name': fields.List(required=True, description='top_benefit'),
    'company': fields.List(required=True, description='search benefit'),
    'front': fields.String(required=True, description='이미지 url'),
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
        pw = request.json["pw"]
        user = account.load_account(con, user_id)
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
    def post(self):
        """회원의 비밀번호와 닉네임을 변경합니다."""
        con = connection.connect_db()
        user_id = request.json["id"]
        pw = request.json["pw"]
        nickname = request.json["nickname"]
        result =  account.update_account(con, user_id, pw, nickname)
        return {
            models.AccountResult.UNSAFE_PASSWORD: (json.dumps({"message": "안전하지 않은 패스워드 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.DUMPLICATED_ID:  (json.dumps({"message": "이미 등록된 아이디 입니다."}, ensure_ascii=False), 401),
            models.AccountResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.AccountResult.SUCCESS:         (json.dumps({"message": "회원가입에 성공하였습니다."}, ensure_ascii=False), 200),
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
        if not hashlib.sha256((userid+pw).encode()).hexdigest() == token:
            return (json.dumps({"message": "비밀번호가 틀렸습니다."}, ensure_ascii=False), 401)
        con = connection.connect_db()
        con.cursor(f"DELETE * FROM accounts WHERE id='{userid}'")
        con.commit()
        print('유저가 성공적으로 제거되었습니다.')
        con.close()
        return (json.dumps({"message": "유저가 성공적으로 제거되었습니다."}, ensure_ascii=False), 200)

# usercards

@usercard_ns.route('/insert')
class InsertCardClass(Resource):
    @usercard_ns.expect(usercard_model)
    def put(self):
        """유저가 등록한 카드 정보를 데이터베이스에 입력합니다"""
        con = connection.connect_db()
        user_id = request.json["id"]
        cardname = request.json["cardname"]

        result = usercard.insert_card(con, cardname, user_id)
        return {
            models.CardResult.FAIL:            (json.dumps({"message": "카드가 이미 존재합니다."}, ensure_ascii=False), 401),
            models.CardResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.CardResult.SUCCESS:         (json.dumps({"message": "카드 등록에 성공하였습니다."}, ensure_ascii=False), 200),
        }[result]

@usercard_ns.route('/withdraw')
class InsertCardClass(Resource):
    @usercard_ns.expect(usercard_model)
    def delete(self):
        """유저가 등록했던 카드 정보를 삭제"""
        con = connection.connect_db()
        user_id = request.json["id"]
        cardname = request.json["cardname"]

        result = usercard.delete_card(con, cardname, user_id)
        return {
            models.CardResult.FAIL:            (json.dumps({"message": "카드가 존재하지 않습니다."}, ensure_ascii=False), 401),
            models.CardResult.SQL_INJECTED:    (json.dumps({"message": "SQL문에 에러가 발생하였습니다."}, ensure_ascii=False), 500),
            models.CardResult.SUCCESS:         (json.dumps({"message": "카드를 성공적으로 제거하였습니다."}, ensure_ascii=False), 200),
        }[result]




if __name__ == "__main__":
    app.run(host='0.0.0.0')