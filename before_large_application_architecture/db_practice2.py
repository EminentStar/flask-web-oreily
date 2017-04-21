from hello import db
from hello import Role, User

"""
Flask-SQLAlchemy는 각 모델 클래스에서 사용 가능한 query 오브젝트를 생성
"""

# 모델을 위한 가장 기본적 ㄱ쿼리는 그에 대응 하는 테이블의 전체 내용을 리턴하는 것
result = Role.query.all()
print("Role.query.all()")
print(result)


result = User.query.all()
print("User.query.all()")
print(result)
user_role = result[0].role

# 쿼리 오브젝트는 filters를 통해 더 정확한 데이터베이스 검색을 실행하도록 설정함.
# "User" 규칙에 할당된 모든 사용자를 검색
result = User.query.filter_by(role=user_role).all()
print('User.query.filter_by(role=user_role).all()')
print(result)


result = User.query.filter().all()
print('User.query.filter().all()')
print(result)


result = User.query.limit(2).all()
print('User.query.limit(2)')
print(result)


result = User.query.filter_by(role=user_role).first()
print('User.query.filter_by(role=user_role).first()')
print(result)

"""
result = User.query.filter_by(username="test").first_or_404()
print('User.query.filter_by(username="test").first()_or_404')
print(result)
"""
result = User.query.filter_by(role=user_role).count()
print('User.query.filter_by(role=user_role).count()')
print(result)


result = User.query.filter().get(1)
print("User.query.filter().get(1)")
print(result)

"""
result = User.query.filter().get_or_404(5)
print("User.query.filter().get_or_404(5)")
print(result)
"""

"""
# user_role.users 쿼리는 사용자의 리스트를 리턴하기 위해 user_role.users 표현이 
# 내부적으로 all()의 호출을 실행할 때 묵시적으로 쿼리가 실행됨
# 그래서 쿼리 오브젝트가 숨겨져 있기 때문에 추가적인 쿼리 필터를 이용하여 개선하는 것을 불가능
users = user_role.users
print(users)
result = user_role.users.order_by(User.username).all() # ERROR!
print('user_role.users.order_by(User.username).all()')
print(result)
"""

"""
# 이걸 해결하기 위해, 관계 설정은 쿼리가 자동으로 실행되지 않도록 리퀘스트하기 위해
# lazy='dynamic'인수로 수정(Role model)
"""
users = user_role.users
print(users)
result = user_role.users.order_by(User.username).all()
print('user_role.users.order_by(User.username).all()')
print(result)

result = user_role.users.count()
print('user_role.users.count()')
print(result)
