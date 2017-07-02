from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import unauthorized, forbidden

# HTTP 기본 일증을 install하기 위해서는 HTTPBasicAuth 클래스의 오브젝트를 생성해야함
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    """
        인증자격이 맞지 않으면 서버는 클라이언트에 401 에러를 리턴한다.
    """
    return unauthorized('Invalid credentials')


"""
login_required 데코레이터는 블루프린트를 위한 before_request 핸들러 안에 한번은 포함되어야 한다.

before_request 핸들러는 계정에 대해 확인되지 않은 인증된 사용자를 거절한다.
"""
@api.before_request
@auth.login_required
def before_request():
    # g: 플라스크의 g 글로벌 오브젝트
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/token')
def get_token():
    # 클라이언트가 새로운 토큰을 리퀘스트할 때 오래된 토큰을 사용하는 것을 막기 위해 
    # g.token_used 변수를 체크함
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token': g.current_user.generate_auth_token(
        expiration=3600), 'expiration': 3600})
