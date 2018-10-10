# Flask app
from flask import Flask, render_template
import datetime
import ssl
from pyexchange import Exchange2010Service, ExchangeNTLMAuthConnection
from random import randint
from secret import SECRET_URL, SECRET_USERNAME, SECRET_PASSWORD

app = Flask(__name__)


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

"""
As of 10/10/18, mailbox connection is not working. Will revisit
"""
def connect(time):
    connection = ExchangeNTLMAuthConnection(url=SECRET_URL,
                                            username=SECRET_USERNAME,
                                            password=SECRET_PASSWORD)
    service = Exchange2010Service(connection)
    my_calendar = service.calendar()
    print(my_calendar)
    events = my_calendar.list_events(
        start=datetime.datetime(time.date().year, time.date().month, time.date().day, time.time().hour, time.time().minute, 0),
        end=datetime.datetime(time.date().year, time.date().month, time.date().day, time.time().hour, time.time().minute+1, 0)
    )
    if events.events == []:
        return "no"
    oof = False
    for event in events.events:
        print(event.subject)
        if event.subject.lower() == "out of office":
            return "ooF"
    return "yes"


def quickfix(time):
    if time.isoweekday() in range(1,5) and time.hour in range(10,11) and time.minute <= 30:
        return "yes"
    if time.isoweekday() == 1 and time.hour in range(13,14):
        return "yes"
    if time.isoweekday() == 2 and time.hour in range(11, 13):
        return "yes"
    if time.isoweekday() == 3 and time.hour in range(16, 17):
        return "yes"
    if time.isoweekday() == 4 and time.hour in range(12, 14):
        return "yes"
    if time.isoweekday() == 5:
        return "oof"
    return "no"


@app.route('/')
def home():
    now = datetime.datetime.now()
    nighttime = now.replace(hour=23, minute=0, second=0, microsecond=0)
    morningtime = now.replace(hour=7, minute=0, second=0, microsecond=0)

    context = {
        "mainString": "No",
        "subString": "He's free right now. You can get in touch."
    }
    context["icon"] = random_icon()
    if now > nighttime or now < morningtime:
        context["mainString"] = "No"
        context["subString"] = "But it IS his night time, so he might not be awake."
    elif now.weekday() > 4:
        context["mainString"] = "No"
        context["subString"] = "But it's a weekend, so he might not be available."
    else:
        #busy = connect(now)
        busy = quickfix(now) #dirtyhack
        if busy == "yes":
            context["mainString"] = "Yes"
            context["subString"] = "But if you drop him an email, he'll get back to you as soon as he can."
        elif busy == "oof":
            context["mainString"] = "No"
            context["subString"] = "But he's out of office, so might not be available"
    return render_template('home.html', context=context)

if __name__ == "__main__":
    app.run(debug=True)
