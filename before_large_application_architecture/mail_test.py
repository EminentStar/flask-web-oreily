from flask.ext.mail import Message
from hello import mail
from hello import app

msg = Message('test subject', sender='junk3843@naver.com', recipients=['junk3843@naver.com'])
msg.body = 'text body'
msg.html = '<b>HTML</b> body'

with app.app_context():
    mail.send(msg)
