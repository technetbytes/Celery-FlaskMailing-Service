from asyncio.windows_events import NULL
import celery
import yaml
import os
import random
import time
from flask import Flask, request, render_template, session, flash, redirect, \
    url_for, jsonify
from flask_mail import Mail, Message
from celery import Celery
from celerycontext import make_celery

# Flask application
flask_app = Flask(__name__)

# Flask E-Mail extension object
mail = None

def get_configuration():
    # Read YAML configuration file
    with open("config.yml","r") as ymlfile:
        cfg = yaml.safe_load(ymlfile)
    return cfg


def set_application_config(config):
    # set secret-key
    flask_app.config['SECRET_KEY'] = config['others']['secret_key']

    # Flask-Mail configuration
    flask_app.config['MAIL_SERVER'] = config['smtp_server']['gateway']
    flask_app.config['MAIL_PORT'] = config['smtp_server']['port']
    flask_app.config['MAIL_USE_TLS'] = config['smtp_server']['tls']
    flask_app.config['MAIL_USERNAME'] = config['smtp_server']['username']
    flask_app.config['MAIL_PASSWORD'] = config['smtp_server']['password']
    flask_app.config['MAIL_DEFAULT_SENDER'] = config['email']['sender']

    # Celery configuration
    flask_app.config['CELERY_BROKER_URL'] = config['task_queue']['celery_broker_url']
    flask_app.config['CELERY_RESULT_BACKEND'] = config['task_queue']['celery_result_backend']

def init_mail():
    # Init extensions
    mail = Mail(flask_app)


print("Initializing Emailing Service ...")
# Load and Set application configuration
set_application_config(get_configuration())
    
# Initialize extensions object
init_mail()

# Initialize object
celery = make_celery(flask_app)

@celery.task
def send_async_email(email_data):
    """Background task to send an email with Flask-Mail."""
    msg = Message(email_data['subject'],
                  sender=flask_app.config['MAIL_DEFAULT_SENDER'],
                  recipients=[email_data['to']])
    msg.body = email_data['body']
    with app.app_context():
        mail.send(msg)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@flask_app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html', email=session.get('email', ''))
    email = request.form['email']
    session['email'] = email

    # send the email
    email_data = {
        'subject': 'Hello from Flask',
        'to': email,
        'body': 'This is a test email sent from a background Celery task.'
    }
    if request.form['submit'] == 'Send':
        # send right away
        send_async_email.delay(email_data)
        flash('Sending email to {0}'.format(email))
    else:
        # send in one minute
        send_async_email.apply_async(args=[email_data], countdown=60)
        flash('An email will be sent to {0} in one minute'.format(email))

    return redirect(url_for('index'))


@flask_app.route('/longtask', methods=['POST'])
def longtask():
    task = long_task.apply_async()
    return jsonify({}), 202, {'Location': url_for('taskstatus',
                                                  task_id=task.id)}


@flask_app.route('/status/<task_id>')
def taskstatus(task_id):
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)



if __name__ == '__main__':
    # run application
    flask_app.run(debug=True)