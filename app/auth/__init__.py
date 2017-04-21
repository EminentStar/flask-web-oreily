"""
사용자 인증 시스템과 관련된 라우트는 auth 블루프린트를 추가할 수 있다.
애플리케이션 기능의 다른 집합을 위해 다른 블루프린트를 사용하는 것은 
코드를 구조적으로 보기 좋게 관리하는 좋은 방법
"""
"""
auth 블루프린트는 같은 이름의 파이썬 패키지에서 호스트함. 
블루프린트의 패키지 생성자는 블루프린트 오브젝트를 생성하고
views.py 모듈에서 라우트를 import한다.
"""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
