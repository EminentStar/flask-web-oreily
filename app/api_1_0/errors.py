from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


""" errorhandler 데코레이터는 http 상태코드를 위한 핸들러를 등록하는 데 사용되는 것이랑 동일함
데코레이터는 API 블루프린트에서 얻는다는 것을 알아두자. 
따라서 이 핸들러는 블루프린트로부터 라우트가 처리되는 동안
예외가 발생할 때만 호출된다.

이걸 사용하게 되면 뷰 함수의 코드는 
에러 체크를 포함할 필요 없이 상당히 깔끔하고 간략하게 작성된다.(posts.py 참조)
"""
@api.errorhandler(ValidationError)
def validation_error(e):
    """ ValidationError 예외를 위한 API 에러 핸들러 """
    return bad_request(e.args[0])
