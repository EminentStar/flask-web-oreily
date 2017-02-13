"""

* flask.ext.moment: 브라우저에서 시간과 날짜를 렌더링하도록 해주는 라이브러리
* flask.ext.wtf: 크로스 사이트 리퀘스트 위조(CSRF) 공격으로부터 모든 폼을 보호
  - CSRF 공격: 악의적 웹사이트에서 희생자가 로그인한 다른 웹사이트로 리퀘스트를 전송할 때 일어남
    - CSRF 보호를 구현하기 위해 Flask-WTF는 암호화 키를 설정하기 위한 앱이 필요
    -  Flask-WTF는 이 키를 사용하여 암호화된 토큰을 생성하고 이 토큰은 폼 데이터와 함께 리퀘스트
       인증을 검증하는데 사용됨.
"""
from datetime import datetime
from flask.ext.script import Manager
from flask import Flask, render_template
from flask import request
from flask import redirect
from flask import abort
from flask.ext.bootstrap import Bootstrap
from flask import url_for
from flask.ext.moment import Moment

from flask.ext.wtf import FlaskForm
from wtforms import StringField, SubmitField 
from wtforms.validators import Required


"""
Flask 클래스 생성자에 필요한 인수는 "메인모듈의 이름" 혹은 "애플리케이션의 패키지 이름"
대부분의 애플리케이션에서는 파이썬의 __name__ 변수가 적절한 값임
플라스크는 이 인수를 사용하여 앱의 루트 패스를 결정하게 되고 따라서 나중에 앱의 위치에 상대적인
리소스 파일들을 이경로를 통해 찾을 수 있다.

__name__: 현재 모듈의 이름을 담고있는 내장 변수

해당 모듈이 python 모듈명.py 와 같이 직접 실행되는 경우에만 __name__은 __main__으로 설정됨
"""
app = Flask(__name__)
manager = Manager(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECKET_KEY'] = '87sh5#(6ui)(!lr#091+8iu2k^=az-6ac+sszj48issc!lu%=j' # 암호화 키 설정 방법


"""
라우트: URL을 파이썬 함수에 매핑하는 기능
app.route 데코레이터를 사용한다.
"""
#@app.route('/')
# methods가 주어지지 않으면 뷰 함수는 GET 리퀘스트만 처리하도록 등록된다.
@app.route('/', methods=['GET', 'POST'])
def index():
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
        name = form.name.data
        form.name.data = ''
    
    return render_template('index.html', form=form, name=name)



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



# Form Class 정의
class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')





if __name__ == '__main__':
    # app.run(debug=True)
    manager.run() # On Terminal, run the app with "python hello.py runserver --host 0.0.0.0"
