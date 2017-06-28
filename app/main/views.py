from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app

from .. import db
from ..models import User, Permission
from ..email import send_email
from . import main
from .forms import NameForm
from app.decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session['known'] = False
            # 새로운 이름이 폼과 함께 수신될때마다 관리자에게 이메일을 전송하도록 확장가능
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        form.name.data = ''
        return redirect(url_for('.index'))
    return render_template('index.html',
        form = form, name = session.get('name'),
        known = session.get('known', False),
        current_time=datetime.utcnow())


# 인증된 사용자에게만 액세스되도록 라우트를 보호하기 위해서,
# Flask-Login은 login_required 데코레이터를 제공함
from flask_login import login_required
@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"

