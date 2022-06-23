from enum import Enum


class Account:
    def __init__(self, id: str, pw: str, nickname: str, tel: str) -> None:
        self.__id = id
        self.__pw = pw
        self.__nickname = nickname
        self.__tel = tel

    @property
    def id(self):
        return self.__id

    @property
    def pw(self):
        return self.__pw
    
    @property
    def nickname(self):
        return self.__nickname

    @property
    def tel(self):
        return self.__tel

    def __str__(self) -> str:
        return f"id: {self.id}, pw: {self.pw}, nickname: {self.nickname}, tel:{self.tel}"


class AccountResult(Enum):
    SUCCESS = 0
    UNSAFE_PASSWORD = 1
    SQL_INJECTED = 2
    NO_USER = 3
    DUMPLICATED_ID = 4
    FAIL = 5

class CardResult(Enum):
    SUCCESS = 0
    FAIL = 1
    SQL_INJECTED = 2

class UserCardResult(Enum):
    SUCCESS = 0
    FAIL = 1
    SQL_INJECTED = 2
    NO_USER = 3
    
class BenefitResult(Enum):
    SUCCESS = 0
    FAIL = 1
    SQL_INJECTED = 2