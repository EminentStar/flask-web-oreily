#!/usr/bin/env python
import os
from app import create_app, db
from app.models import User, Role, Permission, Post, Follow, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

"""
make_shell_context()가 뭐하는 거였는지 다시 파악해보자.
"""
def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, 
                Post=Post, Follow=Follow, Comment=Comment)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

# 테스트를 위한 커스텀 커맨드를 추가
# 데코레이터 함수의 이름은 커맨드 이름으로 사용됨.
# ex) $ python manage.py test
@manager.command
def test(): 
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    manager.run()
