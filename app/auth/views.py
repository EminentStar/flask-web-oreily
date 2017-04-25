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
from ..email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
        PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm

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


"""
"""
@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))

"""
블루프린트로부터 before_request 후크는 블루프린트에 속한 리퀘스트에만 적용됨.
블루프린트로부터 모든 애플리케이션 리퀘스트를 위한 후크를 설치하기 위해서는
before_app_request 데코레이터를 사용해야함.

* before_app_request 핸들러는 세 가지 조건이 참일 때 리퀘스트를 가로챔
1. 로그인되었을 때(current_user.is_authenticated()가 True를 리턴해야함)
2. 사용자가 확인되지 않은 계정
3. 리퀘스트의 종단점(request.endpoint로 액세스 가능)이 인증 블루프린트의 밖에 존재할때 인증
라우트에 대한 액세스가 허용되면 사용자는 계정을 확인하고 계정의 다른 관리 함수들을 수행할 수 있게
된다.
"""
@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
                return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect('main.index')
    return render_template('auth/unconfirmed.html')


"""
이 라우트는 current_user를 사용하여 등록 라우트를 완료하는 작업을 반복한다.
로그인한 사용자는 타깃 사용자가 된다.
이 라우트는 또한 login_required를 사용하여 라우트를 액세스할 때 보호하도록 하며 이 리퀘스트를 만드는
사용자는 알려져있다.
"""
@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email('auth/email/confirm',
               'Confirm Your Account', user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request._args.get('next'))
        flash('An email with instructions to reset your password has been '
                'send to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('main.index'))
        if user.reset_password(token, form.password.data):
            flash('Your password has been updated.')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, 'Confirm your email address',
                    'auth/email/change_email',
                    user=current_user, token=token)
            flash('An email with instructions to confirm your new email '
                  'address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password.')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash('Your email address has been updated.')
    else:
        flash('Invalid request.')
    return redirect(url_for('main.index'))
