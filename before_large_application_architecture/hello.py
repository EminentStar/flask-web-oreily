"""

* flask.ext.moment: 브라우저에서 시간과 날짜를 렌더링하도록 해주는 라이브러리
* flask.ext.wtf: 크로스 사이트 리퀘스트 위조(CSRF) 공격으로부터 모든 폼을 보호
  - CSRF 공격: 악의적 웹사이트에서 희생자가 로그인한 다른 웹사이트로 리퀘스트를 전송할 때 일어남
    - CSRF 보호를 구현하기 위해 Flask-WTF는 암호화 키를 설정하기 위한 앱이 필요
    -  Flask-WTF는 이 키를 사용하여 암호화된 토큰을 생성하고 이 토큰은 폼 데이터와 함께 리퀘스트
       인증을 검증하는데 사용됨.
* flash: 사용자에게 상태 업데이트를 전달하는 메시지를 구성할 수 있는 모듈
"""
import os
from datetime import datetime
from flask_script import Manager
from flask import Flask, render_template
from flask import request
from flask import redirect
from flask import abort
from flask_bootstrap import Bootstrap
from flask import url_for
from flask_moment import Moment
from flask import session
from flask import flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField 
from wtforms.validators import Required

# 쉘 세션이 시작될 때마다 디비 인스턴스 및 모델을 임포트하는 반복을 피하기 위해 사용. 
# 특정 오브젝트를 자동으로 임포트하기 위해 설정. make_context 콜백 함수를 이용하여 등록해야함.
from flask_script import Shell

# Flask- Migrate 설정
from flask_migrate import Migrate, MigrateCommand

# Flask-Mail 초기화
from flask_mail import Mail

# 이메일 지원
from flask_mail import Message

# 이메일 비동기 처리를 위한 Thread
from threading import Thread

"""
Flask 클래스 생성자에 필요한 인수는 "메인모듈의 이름" 혹은 "애플리케이션의 패키지 이름"
대부분의 애플리케이션에서는 파이썬의 __name__ 변수가 적절한 값임
플라스크는 이 인수를 사용하여 앱의 루트 패스를 결정하게 되고 따라서 나중에 앱의 위치에 상대적인
리소스 파일들을 이경로를 통해 찾을 수 있다.

__name__: 현재 모듈의 이름을 담고있는 내장 변수

해당 모듈이 python 모듈명.py 와 같이 직접 실행되는 경우에만 __name__은 __main__으로 설정됨
"""
app = Flask(__name__)

"""데이터베이스 설정"""
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

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



manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'hard to guess' # 암호화 키 설정 방법


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)

manager.add_command("shell", Shell(make_context=make_shell_context))

# Flask- Migrate 설정
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 지메일을 위한 Flask-Mail 설정
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
"""
스크립트에 직접 계정정보를 작성하지 말 것. 오픈소스로 공개할 계획이라면 절대 작성X.
계정 정보를 보호하기 위해 스크립트는 환경에서 민감한 정보를 임포트한다.
이메일 서버 사용자 이름과 패스워드를 보관하는 2개의 환경 변수를정의해야만 함.
배시(bash)를 사용하는 리눅스나 Mac OS X를 사용한다면 다음과 같이 변수들을 설정 가능
$ export MAIL_USERNAME=<Gmail username>
$ export MAIL_PASSWORD=<Gmail password>
"""
# os.environ.get(var)는 환경변수를 불러오는 함수
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME') 
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'

app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to, subject, template, **kwargs):
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
            sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr

# Flask-Mail 초기화
mail = Mail(app)

# Form Class 정의
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            # 새로운 이름이 폼과 함께 수신될때마다 관리자에게 이메일을 전송하도록 확장가능
            if app.config['FLASKY_ADMIN']:
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
        form = form, name = session.get('name'),
        known = session.get('known', False))


"""
라우트: URL을 파이썬 함수에 매핑하는 기능
app.route 데코레이터를 사용한다.
"""
#@app.route('/')
# methods가 주어지지 않으면 뷰 함수는 GET 리퀘스트만 처리하도록 등록된다.
@app.route('/index_first', methods=['GET', 'POST'])
def index_first():
    print("index: " + url_for('index', _external=True))
    print("user: " + url_for('user', name='junkyu', _external=True ))
    print("dict_view: " + url_for('dict_view', _external=True))
    print("list_view: " + url_for('list_view', _external=True))
    print("list_idx_view: " + url_for('list_idx_view', idx=2, _external=True))
    print("if_view: " + url_for('if_view', _external=True))
    print("for_view: " + url_for('for_view', _external=True))
    print("macro_view: " + url_for('macro_view', _external=True))
    print("num: " + url_for('num', id=1,  _external=True))
    print("userAgent: " + url_for('userAgent', _external=True))
    print("redirectPage: " + url_for('redirectPage', _external=True))
    print("aboutPage: " + url_for('aboutPage', _external=True))

    print("index/?page=2: " + url_for('index', page=2, _external=True))

    print("static: " + url_for('static', filename='css/styles.css', _external=True))

    # return '<p>Hello World!</p>'
    # return render_template('index.html')
    # return render_template('index.html', current_time=datetime.utcnow())
    name = None
    form = NameForm()
    # form이 submit될 때 True를 리턴하고 데이터는 모든 필드 검증자에 의해 받아들여지게 된다.
    if form.validate_on_submit():
        """
        name = form.name.data
        form.name.data = ''
        """
        """
        session['name'] = form.name.data
        return redirect(url_for('index'))
        """
        old_name = session.get('name')
        if old_name is not None and old_name != form.name.data:
            flash('Looks like you have changed yourname!')
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('index'))
    return render_template('index.html',
        form = form, name = session.get('name'))


    return render_template('index.html', form=form, name=session.get('name'))
    # return render_template('index.html', form=form, name=name)



"""
동적 이름 컴포넌트를 갖는 라우트 정의
뷰 함수가 실행되면 플라스크는 동적 컴포넌트를 인수로 전송한다.
"""
@app.route('/user/<name>')
def user(name):
    # return '<p>Hello %s</p>' % name 
    return render_template('user.html', name=name)


@app.route('/dict')
def dict_view():
    dic = {'key': 'This is value'}
    return render_template('dict.html', mydict=dic)


@app.route('/list')
def list_view():
    l = []
    l.append('one')
    l.append('two')
    l.append('three')
    l.append('four')
    
    return render_template('list.html', mylist=l)


@app.route('/list/<int:idx>')
def list_idx_view(idx):
    l = []
    l.append('one')
    l.append('two')
    l.append('three')
    l.append('four')
    return render_template('list.html', mylist=l, myintvar=idx)


@app.route('/if')
def if_view():
    # user = 'junkyu'
    # return render_template('if.html', user=user)
    return render_template('if.html')


@app.route('/for')
def for_view():
    comments = []
    comments.append('Hello world')
    comments.append("I'm software maestro")
    comments.append('How is it going?')
    return render_template('for.html', comments=comments)


@app.route('/macro')
def macro_view():
    comments = []
    comments.append('Hello world')
    comments.append("I'm software maestro")
    comments.append('How is it going?')
    return render_template('macro.html', comments=comments)


@app.route('/macro_import')
def macro_import_view():
    comments = []
    comments.append('Hello world')
    comments.append("I'm software maestro")
    comments.append('How is it going?')
    return render_template('macro_import.html', comments=comments)

"""
플라스크는 라우트에 대해 int, float, path를 지원한다.
"""
@app.route('/num/<int:id>')
def num(id):
    return '<h1>number %s</h1>' % id



"""
"""
@app.route('/userAgent')
def userAgent():
    user_agent = request.headers.get('User-Agent')
    return '<p>Your browser is %s</p>' % user_agent



@app.route('/redirect')
def redirectPage():
    return redirect('http://www.naver.com')


@app.route('/abort')
def aboutPage():
    return abort(404)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500








if __name__ == '__main__':
    # app.run(debug=True)
    manager.run() # On Terminal, run the app with "python hello.py runserver --host 0.0.0.0"
