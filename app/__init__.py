from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_pagedown import PageDown
from config import config


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()

# Flask-Login을 애플리케이션 팩토리 함수에서 초기화 가능
from flask_login import LoginManager

login_manager = LoginManager()
# LoginManager 오브젝트의 session_protection속성은 None, 'basic', 혹은 'string'으로 설정가능하다.
# 이는 사용자 세션의 보안 위협에 대해 서로 다른 레벨의 보안성을 제공함.
# 'strong'으로 설정되면 Flask-Login은 클라이언트의 IP주소와 브라우저의 에이전트를 저장하고 저장하고
# 있는 데이터에 변경 사항이 생기면 사용자를 로그아웃시킨다.
login_manager.session_protection = 'strong'
# login_view 속성은 로그인 페이지를 위한 엔드 포인트를 설정한다.
# 로그인 라우트가 블루프린트 안에 있기 때문에 블루프린트 이름 앞에 접두어가 필요하다
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    pagedown.init_app(app)

    # 여기에 라우트와 커스텀 에러 페이지를 추가한다.
    from .main import main as main_blueprint # main package의 __init__.py의 main
    app.register_blueprint(main_blueprint)

    # auth 블루프린트를 create_app() 팩토리에 있는 앱에 부착될 필요가 있음
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    return app

