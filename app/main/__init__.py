# 블루프린트 생성
# 블루프린트는 라우트를 정의하고 있는 애플리케이션과 비슷
# 차이점은 블루프린트와 관련된 라우트는 불루프린트가 애플리케이션과 함께 등록될 때까지
# 휴면 상태라는 점 

from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
