from hello import db
from hello import Role, User

"""
Flask-SQLAlchemy는 각 모델 클래스에서 사용 가능한 query 오브젝트를 생성
"""

# 모델을 위한 가장 기본적 ㄱ쿼리는 그에 대응 하는 테이블의 전체 내용을 리턴하는 것
result = Role.query.all()
print(result)


result = User.query.all()
print(result)
user_role = result[0].role

# 쿼리 오브젝트는 filters를 통해 더 정확한 데이터베이스 검색을 실행하도록 설정함.
# "User" 규칙에 할당된 모든 사용자를 검색
result = User.query.filter_by(role=user_role).all()
print(result)

