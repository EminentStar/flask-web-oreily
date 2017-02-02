from flask.ext.script import Manager
from flask import Flask
from flask import request
from flask import redirect
from flask import abort


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


"""
라우트: URL을 파이썬 함수에 매핑하는 기능
app.route 데코레이터를 사용한다.
"""
@app.route('/')
def index():
    return '<p>Hello World!</p>'




"""
동적 이름 컴포넌트를 갖는 라우트 정의
뷰 함수가 실행되면 플라스크는 동적 컴포넌트를 인수로 전송한다.
"""
@app.route('/user/<name>')
def user(name):
    return '<p>Hello %s</p>' % name 


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



if __name__ == '__main__':
    # app.run(debug=True)
    manager.run() # On Terminal, run the app with "python hello.py runserver --host 0.0.0.0"
