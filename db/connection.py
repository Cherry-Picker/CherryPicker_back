import pymysql


def connect_db():
    try:
        connection = pymysql.connect(
            host = '118.67.133.146',
            user = 'cherry',
            password = 'cherry',
            charset='utf8',
            db='cherrypicker'
        )
        print('데이터베이스에 성공적으로 연결되었습니다.')
    except pymysql.Error:
        print('데이터베이스에 연결을 실패하였습니다.')
        assert pymysql.Error
    return connection
