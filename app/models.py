from . import db


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

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id')) 
    password = db.Column(db.String(20))

    def __repr__(self):
        return '<User %r>' % self.username

