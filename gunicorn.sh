#!/bin/bash
 
NAME="flask_app"
# FLASKDIR=/home/ubuntu/FLASK
# SOCKFILE=/home/ubuntu/FLASK/sock
USER=junkyu
GROUP=staff
NUM_WORKERS=5
 
echo "Starting $NAME"
 
# Create the run directory if it doesn't exist
# RUNDIR=$(dirname $SOCKFILE)
# test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your gunicorn
# EXAMPLE: 
#   wsgi:manager
#   colon의 왼쪽(wsgi)은 애플리케이션을 정의하는 패키지나 모듈
#   colon의 오른쪽(manager)은 애플리케이션 인스턴스의 이름
exec gunicorn wsgi:manager -b 0.0.0.0:8080 \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
#  --bind=unix:$SOCKFILE
