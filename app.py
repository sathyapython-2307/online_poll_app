from flask import Flask, render_template, request, jsonify, flash, redirect, session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretpollkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///poll.db'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Session(app)
db = SQLAlchemy(app)
CORS(app)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=False)
    options = db.relationship('Option', backref='poll', lazy=True)

class Option(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    votes = db.Column(db.Integer, default=0)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)

def setup():
    with app.app_context():
        db.create_all()
        if not Poll.query.first():
            sample_poll = Poll(question="What's your favorite programming language?")
            db.session.add(sample_poll)
            db.session.commit()

            sample_options = [
                Option(text='Python', poll_id=sample_poll.id),
                Option(text='JavaScript', poll_id=sample_poll.id),
                Option(text='Java', poll_id=sample_poll.id),
                Option(text='C++', poll_id=sample_poll.id),
            ]
            db.session.add_all(sample_options)
            db.session.commit()

setup()

@app.route('/')
def index():
    poll = Poll.query.first()
    options = Option.query.filter_by(poll_id=poll.id).all()
    return render_template('index.html', poll=poll, options=options)

@app.route('/api/poll')
def get_poll():
    poll = Poll.query.first()
    options = Option.query.filter_by(poll_id=poll.id).all()
    return jsonify({
        'question': poll.question,
        'options': [{'id': o.id, 'text': o.text, 'votes': o.votes} for o in options]
    })

@app.route('/api/vote', methods=['POST'])
def vote():
    if session.get('voted'):
        return jsonify({'error': 'You have already voted'}), 403

    data = request.get_json()
    option_id = data.get('option_id')
    option = Option.query.get(option_id)
    if option:
        option.votes += 1
        db.session.commit()
        session['voted'] = True
        flash('Vote submitted!', 'success')
        return jsonify({'message': 'Vote recorded'})
    return jsonify({'error': 'Option not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
