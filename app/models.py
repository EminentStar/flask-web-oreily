from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import UserMixin

# Flask-Login은 사용자와 주어진 인식자를 로드하는 콜백함수를 셋업하게 됨
# 사용자 로더 콜백 함수는 사용자 인식자를 유니코드 문자열로 받는다.
# 이 함수의 리턴값은 사용 가능하다면 사용자 오브젝트가 되어야하며,
# 그렇지 않다면 None이 되어야 한다
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


"""데이터베이스 모델 정의"""
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    # 관계 설정은 쿼리가 자동으로 실행되지 않도록 리퀘스트하기 위해 lazy='dynamic'으로
    # users = db.relationship('User', backref='role') 
    users = db.relationship('User', backref='role', lazy='dynamic') 

    def __repr__(self):
        return '<Role %r>' % self.name

"""
User 모델을 사용해 로그인을 작업하려면 Flask-Login 확장은
구현할 몇가지 메소드가 필요
* methods
  - is_authenticated(): 사용자가 로그인 자격을 갖고 있다면 True
  - is_active(): 사용자에게 로그인이 허용된다면 True
  - is_anonymous(): 일반적인 사용자에겐 항상 False
  - get_id(): 사용자의 고유 인식자를 리턴하는데 이 값은 유니코드 문자열로 인코딩

그런데 더 쉬운 방법으로 Flask-Login은 대부분의 경우에 적합한 기본 구현을 
이미 갖고 있는 UserMixin을 제공한다.
"""
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) 
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username
