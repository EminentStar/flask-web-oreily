from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, AnonymousUserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app, request, url_for
from datetime import datetime
import hashlib
from markdown import markdown
import bleach
from app.exceptions import ValidationError


from . import db

# Flask-Login은 사용자와 주어진 인식자를 로드하는 콜백함수를 셋업하게 됨
# 사용자 로더 콜백 함수는 사용자 인식자를 유니코드 문자열로 받는다.
# 이 함수의 리턴값은 사용 가능하다면 사용자 오브젝트가 되어야하며,
# 그렇지 않다면 None이 되어야 한다
from . import login_manager

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    disabled = db.Column(db.Boolean) # 적절하지 않은 코멘트를 관리하기 위함.
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        target_body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_comment = {
            'url': url_for('api.get_comment', id=self.id, _external=True),
            'post': url_for('api.get_post', id=self.post_id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment):
        body = json_comment.get('body')
        if body is None or body == '':
            raise ValidationError('comment does not have a body')
        return Comment(body=body)

db.event.listen(Comment.body, 'set', Comment.on_changed_body)


class Follow(db.Model):
    """
        관계에서 커스텀 데이터를 사용하기 위해서 관련 테이블이 애플리케이션에서 액세스될 수 있도록
        적절한 모델이 되어야 함.
    """
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


"""데이터베이스 모델 정의"""
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    # 관계 설정은 쿼리가 자동으로 실행되지 않도록 리퀘스트하기 위해 lazy='dynamic'으로
    # users = db.relationship('User', backref='role') 
    users = db.relationship('User', backref='role', lazy='dynamic') 

    def __repr__(self):
        return '<Role %r>' % self.name
    
    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT | 
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                     Permission.COMMENT | 
                     Permission.WRITE_ARTICLES | 
                     Permission.MODERATE_COMMENTS, False),
            'Admistrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

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
    confirmed = db.Column(db.Boolean, default=True) 
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text()) # db.String과의 차이는 db.Text는 최대 길이가 필요하지 않다는 점
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    """
        lazy='dynamic' 모드는관계 속성은 직접 아이템을 리턴하지 않고 쿼리 오브젝트를 리턴한다. 또한
        추가적인 필터가 실행되기 전에 쿼리가 추가됨.
    """
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    """
        관계는 일대다 관계를 위해사용된 동일한 db.relationship() 생성으로 정의됨
        그러나 다대다 관계인 경우 추가적으로 secondary 인수가 관련 테이블을 설정해줘야함.
        관계는 두 개의 클래스 각각을 정의하며 backref 인수를 사용하여 다른 쪽의 관계를 연결해 준다.
        다다다의 경우 association table을 추가하면 됨. 이는 테이블로 정의되지만 모델은 아님.
        SQLAlchemy가 이 테이블을 내부적으로 관리함.
    """
    """
        followed, followers는 각각 일대다 관계로 정의되었음.
        역참조를 위한 lazy 인수는 joined로 설정됨. 
        이 lazy mode는 관련된 오브젝트가 조인 쿼리로부터 즉시 로드되도록 한다.
        lazy의기본값은 select인데, user.followed.all()을 호출하면 100개의 Follow 인스턴스를 리턴하게
        되며 각각은 followers와 followed 역참조 속석을 각자의 사용자로 설정하도록 한다. 이때 팔로워한 사용자의 완전한 리스트를 얻는다는 것은 100개의 추가적인 데이터베이스
        쿼리를 원한다는 것을 의미함. 
        하지만 lazy='joined'는 user.followed.all()을 호출할때 하나의 데이터베이스 쿼리에서
        발생하도록 한다.
        cascade 인수는 부모 오브젝트에서 수행된 액션이 관련되어 있는 오브젝트에 어떻게 전파하는지를
        설정한다. 이 옵션의 예는 오브젝트가 디비 세션에 추가될 때 적용되는 규칙이며 관련된 관례를
        통해서 어떤 오브젝트라도 자동으로 세션에 추가되어야 한다. 디폴트 cascade 옵션은 대부분의
        상황에서 적합하지만, 다대다 관계의 경우 적합하지 않다.
        오브젝트가 삭제될 때 default cascade 옵션의 행동은 null 값으로 링크되어 있는 관련된
        오브젝트에서 외래키를 설정하는 것이다. 그러나 관련 테이블의 경우 올바른 행동은 삭제할
        레코드를 가리키는 엔트리를 삭제하는 것이며 이것은 링크를 효과적으로 없애게 된다. 이와 같은
        작업은 delete-orphan cascade 옵션이 하는 작업이다.
    """
    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    # comments 테이블을 사용하여 일대다 관계 정의
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        self.followed.append(Follow(followed=self))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})
    
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})
    
    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True
    
    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})
    

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
                (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
                self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    confirmed=True,
                    name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence(),
                    member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    
    @staticmethod
    def add_self_follows():
        """
            이렇게 데이터베이스에 업데이트하도록 하는 함수를 생성하는 것은 애플리케이션을 배포할 때
            애플리케이션을 업데이트하려고 사용되는 일반적인 기술임.
            ```
                $ python manage.py shell
                >> User.add_self_follows()
            ```
        """
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)


    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        return self.followed.filter_by(
                followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        return self.followers.filter_by(
                follower_id=user.id).first() is not None

    @property
    def followed_posts(self):
        """
            이 메소드는 property로 정의되기에 ()가 필요없다.
        """
        """
            해당 유저가 following한 사용자가 작성한 블로그 포스트의 리스트
        """
        return Post.query.join(Follow, Follow.followed_id == Post.author_id)\
                .filter(Follow.follower_id == self.id)
    
    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            'followed_posts': url_for('api.get_user_followed_posts',
                                      id=self.id, _external=True),
            'post_count': self.posts.count()
        }
        return json_user

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('ascii')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # comments 테이블을 사용하여 일대다 관계 정의
    comments = db.relationship('Comment', backref='post', lazy='dynamic')

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                    timestamp=forgery_py.date.date(True),
                    author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, intiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

    def to_json(self):
        json_post = {
            'url': url_for('api.get_post', id=self.id, _external=True),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author': url_for('api.get_user', id=self.author_id,
                              _external=True),
            'comments': url_for('api.get_post_comments', id=self.id,
                                _external=True),
            'comment_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        if body is None or body == '':
            raise ValidationError('post does not have a body')
        return Post(body=body)

"""
on_changed_body 함수는 보디(body)의 SQLAlchemy의 'set' 이벤트의 listener로 등록됨.
이는 클래스의 어떤 인스턴스에서도 body 필드가 새로운 값으로 설정되면 자동으로 호출된다는 의미. 이
함수는 body의 html 버전을 렌더링하고 마크다운 텍스트를 HTML의 자동 변환을 효과적으로 하는
body_html에 저장하게 됨.

## 실제 변환작업
1. markdown()이 HTML로 촉기 변환 작업을 함. 그 결과 승인된 HTML 태그의 리스트와 함께 clean에 전달됨
2. clean()은 white list에 없는 태그를 삭제함.
3. 마지막 변환 작업은 bleach의 linkify()를 사용해서 이뤄짐.
"""
db.event.listen(Post.body, 'set', Post.on_changed_body)

login_manager.anonymous_user = AnonymousUser


