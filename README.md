# Back-end

### Developer
- HyunP-dev
- rlaxogh5079 

* * * 

### Summary

1. requests와 bs4, json을 이용하여 대형 카드 플랫폼으로 부터 정보를 추출 및 가공


2. 추출한 정보를 Flask 프레임워크를 이용해 REST API를 구축함으로써 DB 조작을 수월하게 함.


* * *

### Technical

- 백엔드와 프론트엔드를 완벽히 분리한 대신 백엔드 단에서 Swagger를 통해 코드 리뷰 없이 백엔드를 사용할 수 있을 정도로의 문서화.

- docker-compose를 통해서 카드 관련 모든 crawler를 백그라운드에서 계속 실행 (restart:always)

- 카드의 이름을 검색할때, 유사한 이름의 카드까지 조회하는 것을 한국어의 자모체계를 고려해 자모를 분리하여 levenshtein distance function을 이용하였습니다.

* * *

### Quetions

#### - 데이터는 어떻게 추출하고 가공하였는가?<br>
    데이터는 국내 카드 플랫폼 "카드 고릴라"를 위주로 크롤링 하였습니다.
    "카드 고릴라"로 부터 불러온 정보들은 다음과 같습니다
    1. 카드의 기본적인 정보
    2. 카드별 기본적으로 제공하는 혜택
    3. 카드별 현재 진행하고 있는 이벤트
    
    추가적으로 데이터 베이스의 정보는 다음과 같습니다
    
<image src="./images/cherrypicker.svg"></image>
    
#### - Flask를 사용한 이유<br>
    복잡한 API 개발이 아니기 때문에, 다른 프레임워크들에 비해 가벼운 Flask를 사용하는 것이 적합하다 판단했습니다.