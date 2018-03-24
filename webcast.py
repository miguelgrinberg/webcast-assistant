import json
import os
import random
from threading import Thread
from dotenv import load_dotenv
from flask import Flask, jsonify, session, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, static_url_path='', static_folder='client/build')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'shhhh!!!')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(
    os.path.join(basedir, 'db.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GITTER_TOKEN'] = os.environ.get('GITTER_TOKEN')
app.config['GITTER_ROOM'] = os.environ.get('GITTER_ROOM')
app.config['GITTER_PREFIX'] = os.environ.get('GITTER_PREFIX', 'question:')
app.config['ADMIN_TOKEN'] = os.environ.get('ADMIN_TOKEN')
db = SQLAlchemy(app)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(32), nullable=False)
    votes = db.Column(db.Integer, index=True, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'author': self.author,
            'votes': self.votes,
            'upvoted': self.id in session['votes']
        }


def get_gitter_room_id():
    # get rooms
    rv = requests.get(
        'https://api.gitter.im/v1/rooms',
        headers={'Authorization': 'Bearer ' + app.config['GITTER_TOKEN']})
    rv.raise_for_status()
    room_id = None
    for room in rv.json():
        if room['name'] == app.config['GITTER_ROOM']:
            room_id = room['id']
            break
    if room_id is None:
        raise RuntimeError('cannot find gitter room!')
    return room_id


def gitter_stream():
    room_id = get_gitter_room_id()
    rv = requests.get(
        'https://stream.gitter.im/v1/rooms/' + room_id + '/chatMessages',
        headers={'Authorization': 'Bearer ' + app.config['GITTER_TOKEN']},
        stream=True)
    rv.raise_for_status()
    for line in rv.iter_lines(decode_unicode=True):
        try:
            msg = json.loads(line)
        except:
            continue
        if msg['html'].lower().startswith(app.config['GITTER_PREFIX']):
            q = Question(
                question=msg['html'][len(app.config[
                    'GITTER_PREFIX']):].strip(),
                author=msg['fromUser']['username'], votes=1)
            with app.app_context():
                db.session.add(q)
                db.session.commit()


def gitter_thread():
    while True:
        try:
            gitter_stream()
        except BaseException as e:
            print('{} error, restarting thread'.format(e))
        else:
            print('thread exited, restarting')


@app.before_request
def before_request():
    if 'votes' not in session:
        session['votes'] = []


@app.before_first_request
def initialize():
    db.create_all()
    th = Thread(target=gitter_thread)
    th.daemon = True
    th.start()


@app.route('/')
def index():
    return redirect('/index.html')


@app.route('/api/questions', methods=['GET'])
def get_questions():
    return jsonify([
        q.to_dict() for q in Question.query.order_by(Question.votes.desc())])


@app.route('/api/questions/<int:id>', methods=['POST'])
def vote_question(id):
    if id not in session['votes']:
        q = Question.query.get_or_404(id)
        session['votes'].append(id)
        session.modified = True
        q.votes += 1
        db.session.commit()
    return '', 204


@app.route('/api/giveaways', methods=['POST'])
def giveaway():
    """Select a random user from those who are online in the gitter room."""
    if request.headers.get('Authorization') != 'Bearer {}'.format(
            app.config['ADMIN_TOKEN']):
        return jsonify({'error': 'Missing token'}), 401
    product = request.get_json().get('product')
    if product is None:
        return jsonify({'error': 'Missing product'}), 400

    room_id = get_gitter_room_id()
    rv = requests.get(
        'https://api.gitter.im/v1/rooms/' + room_id + '/users',
        headers={'Authorization': 'Bearer ' + app.config['GITTER_TOKEN']})
    rv.raise_for_status()
    users = [user['username'] for user in rv.json()
             if user.get('role') != 'admin']
    winner = random.choice(users)
    rv = requests.post(
        'https://api.gitter.im/v1/rooms/' + room_id + '/chatMessages',
        headers={'Authorization': 'Bearer ' + app.config['GITTER_TOKEN']},
        json={'text': 'Congratulations, @{}, you are the winner of {}!'.format(
            winner, product)})
    return '', 204
