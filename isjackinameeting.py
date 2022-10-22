# Flask app
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import ssl
from random import randint
import secret

app = Flask(__name__)

db_string = 'mysql+pymysql://' + secret.DB_USERNAME + ':' + secret.DB_PASSWORD + '@' + secret.DB_HOST + '/' + secret.DB_NAME
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['APPLICAITON_ROOT'] = '/'
app.config['WTF_CSRF_ENABLED'] = True
app.config['SECRET_KEY'] = "secret"
db = SQLAlchemy(app)

class CheckIn(db.Model):
    __tablename__ = 'in_table'

    name = db.Column(db.String(225), primary_key=True)
    inmeeting = db.Column(db.Integer)

    def result(self):
        if self.inmeeting == 0:
            return "free_office"
        elif self.inmeeting == 2:
            return "free_home"
        else:
            return "busy"


def random_icon():
    icons = [
        "empire",
        "rebel",
        "phoenix-squadron",
        "sith",
        "trade-federation",
        "galactic-senate",
        "mandalorian",
        "first-order",
        "first-order-alt",
        "galactic-republic",
        "jedi-order",
        "old-republic"
    ]
    x = randint(0, len(icons)-1)
    return icons[x]


def main_times(time):
    if time.isoweekday() in range(6,8):
        return "weekend"
    if time.hour >= 17 and time.hour < 22:
        return "evening"
    if time.hour >= 22 and time.hour < 5:
        return "night"
    if time.hour >= 5 and time.hour < 9:
        return "morning"
    return None


_responses_ = {
    "weekend": {"mainString":"No","subString":"But it's a weekend, so he might not be available."},
    "free_office":{"mainString": "No","subString": "He's in the office right now. You can pop by and see him or give him a call."},
    "free_home":{"mainString": "No","subString": "But he's not in the office right now. Send him an email."},
    "busy": {"mainString":"Yes","subString":"But if you drop him an email, he'll get back to you as soon as he can."},
    "night": {"mainString": "No","subString": "But it IS his night time, so he might not be awake."},
    "evening": {"mainString": "No","subString": "But it's outside of his usual working hours, so he might not be available"},
    "morning":{"mainString": "No","subString": "But it's early, so he might not be in the office yet."},
}


@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({'message' : 'Hello, World!'})


@app.route('/api/get_status', methods=['GET'])
def api_get_current():
    status = check_status()
    return jsonify({'status' : status})


@app.route('/api/switch', methods=['GET'])
def api_switch(auth):
    # should probbaly fix this...
    auth = request.args.get("auth")
    status = request.args.get("status")
    if auth != secret.API_PASS:
        return jsonify({'message' : 'no auth'})
    switch_status("status")
    return jsonify({'message' : 'success', 'status': status})


def switch_status(status):
    meeting = CheckIn.query.filter_by(name="main").first()
    if status=="busy":
        meeting.inmeeting = 1
    elif status=="free_home":
        meeting.inmeeting = 2
    else:
        meeting.inmeeting = 0
    db.session.commit()
    return meeting.result()


def check_status():
    meeting = CheckIn.query.filter_by(name="main").first()
    return meeting.result()


@app.route('/')
def home():
    now = datetime.datetime.now()
    meeting = main_times(now)
    if meeting:
        context = _responses_[meeting]
    else:
        meeting = check_status()
        context = _responses_[meeting]
    context["icon"] = random_icon()
    return render_template('home.html', context=context)


if __name__ == "__main__":
    app.run(debug=True)
