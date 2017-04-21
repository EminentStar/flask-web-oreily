"""
views.py는 블루프린트를 import하고 route 데코레이터를 사용하여 인증과 관련된 라우트를 정의한다.
"""
from flask import render_template
from . import auth

@auth.route('/login')
def login():
    """
    render_template()안의 템플릿 파일은 auth 폴더에 저장됨.
    이 폴더는 app/template 안에 생성되어야 하며 
    플라스크는 이 템플릿이애플리케이션의 템플릿 폴더가 될 것으로 예상함
    자신의 폴더에 블루프린트 템플릿을 저장하면 main 블루프린트와 이름이
    겹칠 ㅇ위험도 없고 나중에 다른 블루프린트도 추가할 수 있다.
    """
    return render_template('auth/login.html')
