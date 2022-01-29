# from flask import Flask
# from flask_mail import Mail
# from flask_mail import Message


# app = Flask(__name__)
# https://www.youtube.com/channel/UC9eIq7PwD0WA-2B_Sp7xGdw

# app.config['MAIL_SERVER'] = 'gator3021.hostgator.com'
# app.config['MAIL_PORT'] = 465
# app.config['MAIL_USE_TLS'] = True
# app.config['MAIL_USERNAME'] = "saqibullah@markematics.com.pk"
# app.config['MAIL_PASSWORD'] = "_SuZpv!N9BYm"
# app.config['MAIL_DEFAULT_SENDER'] = 'Default sender name'

# mail = Mail(app)

# @app.route('/')
# def hello_world():
    # return 'Hello World!'

# @app.route('/send')
# def send_mail():
    # msg = Message("Hello",
                  # sender="saqibullah@markematics.com.pk",
                  # recipients=["saqibullah@markematics.com.pk"])
    # #mail.send(msg)
    # return "called"

# @app.route('/sending')
# def index():
  # msg = Message('Hello from the other side!', sender =   'saqibullah@markematics.com.pk', recipients = ['saqibullah@markematics.com.pk'])
  # msg.body = "Hey Paul, sending you this email from my Flask app, lmk if it works"
  # mail.send(msg)
  # return "Message sent!"
  

# if __name__ == '__main__':
    # app.run(debug=True)
    
from celery import Celery

app = Celery('tasks', backend='redis://localhost', broker='redis://localhost:6379/0')

@app.task
def add(x, y):
    return x + y  