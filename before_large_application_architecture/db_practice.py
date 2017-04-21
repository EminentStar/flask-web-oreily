from hello import db


"""
데이터베이스가 이미 존재할 경우 
테이블을 새로 생성하거나 업데이트 하지 않기에
데이터베이스를 지우고 다시 만든다.
"""
db.drop_all()
db.create_all() # database 생성


"""행 추가"""
from hello import Role, User
admin_role = Role(name='Admin')
mod_role = Role(name='Moderator')
user_role = Role(name='User')
user_john = User(username='john', role=admin_role)
user_susan = User(username='susan', role=user_role)
user_david = User(username='david', role=user_role)


"""
오브젝트는 단지 파이썬에만 존재하며 아직 데이터베이스는 작성되지 않았다.
id값이 아직 설정되지 않았기 때문
"""
print(admin_role.id)
print(mod_role.id)
print(user_role.id)


""" 데이터베이스에 대한 변경 사항은 데이터베이스 세션을 통해 관리됨. 데이터베이스 작성을 위해
오브젝트를 준비하기 위해서는 오브젝트가 세션에 추가되어야 한다."""
db.session.add(admin_role)
db.session.add(mod_role)
db.session.add(user_role)
db.session.add(user_john)
db.session.add(user_susan)
db.session.add(user_david)

"""이런식으로 한꺼번에 저장이 가능하니, 캐싱했다가 모아서 보내서 성능향상하는 것도 가능할듯?"""
"""
db.session.add_all([admin_role, mod_role, user_role, 
    user_john, user_susan, user_david])
"""

""" 디비에 오브젝트를 작성하기 위해서는 세션이 commit() 메소드를 호출하여 컴닛해야 한다."""
db.session.commit()

print(admin_role.id)
print(mod_role.id)
print(user_role.id)


"""db.session의 add()는 모델을 업데이트하는 데도 사용됨"""

print("Before modifying: %r" % (admin_role.name))
admin_role.name = 'Administrator'
db.session.add(admin_role)
db.session.commit()

print("After modifying: %r" % (admin_role.name))


"""role 삭제"""
print("Before deleting: %r" % (mod_role.id))
db.session.delete(mod_role)
db.session.commit()

print("After deleting: %r" % (mod_role.id))






