# Flask-Oreily





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

