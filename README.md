# Flask-Oreily
**Flask는 경량화라는 특성으로 인해 RESTful 웹 서비스를 구축할 수 있는 이상적인 프레임워크**




### How to initialize Database with manage.py
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
```

### How to add environment variables on the OS
```
$ export FLASKY_ADMIN=<your-email-address>
$ export FLASKY_POSTS_PER_PAGE=<counts>
```

### How to Create Roles at the first time
```
$ python manage.py shell
>> Role.insert_roles()
```

### How to query and remove specific user (example)
```
>> u = User.query.filter_by(username='junkyu').first()
>> db.session.delete(u)
>> db.session.commit()
```

### Generate fake data
```
$ python manage.py shell
>> User.generate_fake(100)
>> Post.generate_fake(100)
```

* python package dependencies
- forgerypy: 가짜 정보를 생성하는 패키지
- flask-pagedown: Flask-WTF 폼을 사용하여 페이지다운(자바스크립트로 구현된 클라이언트 측 markdown-to-HTML 변환기)을 통합한 플라스크의 페이지다운 래퍼
- markdown: 서버측 markdown-to-HTML 변환기
- bleach: HTML sanitizer
- flask-httpauth: HTTP 인증을 위한 래퍼
- httpie: http 클라이언트
- coverage: 코드 커버리지 툴


### HTTPie Usage
```
$ http --json --auth <email>:<password" GET \
> http://127.0.0.1:5000/api/v1.0/posts

$ http --json --auth : GET http://127.0.0.1:5000/api/v1.0/posts/

$ http --auth <email>:<password> --json GET \
> http://127.0.0.1:5000/api/v1.0/token

$ http --json --auth eyJpYXQiOjE0OTkwMjc4NzcsImFsZyI6IkhTMjU2IiwiZXhwIjoxNDk5MDMxNDc3fQ.eyJpZCI6MX0.zxxc-fTH2_rVWowkRgqxxBgxiEmHtiGsROK2vPBpXuE: GET http://127.0.0.1:5000/api/v1.0/posts/
```


## REST

### REST의 6가지 특징
1. Client-Server
    - 클라이언트와 서버는 확실하게 분리되어야 한다.
2. Stateless
    - Client request는 전송하는 데 필요한 모든 정보를 포함해야 한다. 서버는 하나의 리퀘스트와 다음 리퀘스트 간의 서비스를 지속시키기 위해 클라이언트에 대한 어떤 상태 정보도 저장하지 않아야 한다.
3. Cache
    - 서버로부터의 응답은 cacheable 혹은 noncacheable으로 표시되어 클라이언트(혹은 클라이언트와 서버 사이의 중간체)가 최적화 목적으로 캐시를 사용할 수 있어야 한다.
4. Uniform Interface
    - 클라이언트가 서버 리소스를 액세스하는 프로토콜은 일관성을 유지해야 하며, 잘 정의되고 표준화되어야 한다. REST 웹 서비스에서 일반적으로 사용되는 유니폼 인터페이스는 HTTP 프로토콜이다.
5. Layered System
    - 프록시 서버, 캐시나 게이트웨이는 클라이언트와 서버 간의 성능, 신뢰성, 확장성을 향상시키는 데 필요한 요소로 추가될 수 있다.
6. Code-on-Demand
    - Client는 컨텍스트를 실행하기 위해 서버로부터 코드를 선택하여 다운로드할 수 있다.


### REST-Resource
**리소스**의 개념은 REST 아키텍처 스타일의 핵심. 이 프로젝트에서의 사용자, 포스트, 코멘트가 모두 리소스임.

각 리소스는 그 리소스를 표현하는 고유의 URL을 가지고 있어야 함. 예를 들어 포스트의 경우 URL */api/posts/12345*로 표현될 수 있는데, 여기서 12345는 포스트 데이터베이스의 기본키와 같은 포스트를 위한 고유의 식별자가 된다.
`플라스크는 슬래시 기호로 끝나는 라우트를 특별히 처리한다는 점에 유의하라. 클라이언트가 슬래시 기호 없이 URL을 리퀘스트하고 매칭되는 단 하나의 라우트만이 끝에 슬래시 기호가 있다면, 플라스크는 자동으로 끝에 슬래시 기호가 있는 URL로 리다이렉트하는 응답을 한다. (반대의 경우 리다이렉트 하지 않는다.)`


### REST-method
- 클라이언트 앱은 서버에 리퀘스트를 보낼때 원하는 작업을 알려주기 위해 request method를 사용함.


### REST-request/response body
- RESTful web service에서 사용하는 포맷은 JSON(JavaScript Object Notation)과 XML(eXtended Markup Language).
- JSON이 자바스크립트와 더 유사하고 클라이언트 측 스크립트 언어로 웹 브라우저에서 사용되고 있기 때문에 매력적임.


### REST-version
- 웹 서비스는 클라이언트의 구버전과 잘 동작해야 한다. 이를 해결하기 위한 일반적인 방법은 웹서비스에서 처리되는 URL을 버전별로 관리하는 것.
- 서버의 다중 버전을 지원하는 것이 관리 측면에서 부담이 된다고 하더라도, 애플리케이션이 기존의 배포에 문제를 발생시키지 않으면서 성장할 수 있는 유일한 방법.


### HTTP-StatusCode often used
|Code|Name|Descriptions|
|200|OK|리퀘스트가 완전히 성공함|
|201|Created|리퀘스트가 완전히 성공했고 결과로 새로운 리소스가 생성됨|
|400|Bad request|리퀘스트가 올바르지 않거나 일치하지 않음|
|401|Unauthorized|리퀘스트가 인증 정보를 포함하고 있지 않음|
|403|Forbidden|리퀘스트와 함께 전송된 인증 자격이 리퀘스트에 대해 불충분함|
|404|Not found|URL에 참조된 리소스를 찾을 수 없음|
|405|Method not allowed|요청받은 리퀘스트 메소드는 주어진 리소스를 지원하지 않음|
|500|Internal server error|예상하지 못한 에러가 리퀘스트를 처리하는 동안 발생함|
