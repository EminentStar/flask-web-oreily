"""
views.py는 블루프린트를 import하고 route 데코레이터를 사용하여 인증과 관련된 라우트를 정의한다.
"""
from flask import render_template
from . import auth

from flask import redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, \
        current_user
from .. import db
from ..models import User
from .forms import LoginForm
from ..email import send_email
from .forms import LoginForm, RegistrationForm


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """
    render_template()안의 템플릿 파일은 auth 폴더에 저장됨.
    이 폴더는 app/template 안에 생성되어야 하며 
    플라스크는 이 템플릿이애플리케이션의 템플릿 폴더가 될 것으로 예상함
    자신의 폴더에 블루프린트 템플릿을 저장하면 main 블루프린트와 이름이
    겹칠 위험도 없고 나중에 다른 블루프린트도 추가할 수 있다.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))

        flash('Invalid username or password')

    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash('You can now login.')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)
