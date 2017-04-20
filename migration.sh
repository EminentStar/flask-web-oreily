# 디비 마이그레이션이 유지되기 전에 init 서브 커맨드를 사용해 마이그레이션 저장소를 생성
# migrations 디렉토리를 생성함.
python hello.py db init

# 마이그레이션 스크랩트 생성
python hello.py db migrate -m "initial migration"

# 마이그레이션 스크립트를 일단 검토하고 받아들이면, 
# 스크립트는 db upgrade 커맨드를 사용하여 데이터베이스에 적용
python hello.py db upgrade
