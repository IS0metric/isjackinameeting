# Flask app
from __future__ import print_function
from flask import Flask, render_template
app = Flask(__name__)

import datetime
import urllib2
import urllib
import json
from icalendar import Calendar
import os

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def getCalendar():
    with open(os.path.join(__location__, 'secret.json')) as data_file:
        data = json.load(data_file)
    response = urllib.request.urlopen(data["cal_url"]) # CHANGE FOR URLLIB
    calendar = response.read()
    return Calendar.from_ical(calendar)

@app.route('/')
def home():
    calendar = getCalendar()
    now = datetime.datetime.now()
    nighttime = now.replace(hour=23, minute=0, second=0, microsecond=0)
    morningtime = now.replace(hour=7, minute=0, second=0, microsecond=0)

    context = {
        "mainString": "NO",
        "subString": "He's free right now. You can get in touch."
    }

    if now > nighttime and now < morningtime:
        context["mainString"] = "NO..."
        context["subString"] = "...but it IS his night time, so he might not be awake."
    else:
        for component in calendar.walk():
            if component.name == "VEVENT":
                start = component.get("dtstart").dt.replace(tzinfo=None)
                end = component.get("dtend").dt.replace(tzinfo=None)
                if now > start and now < end:
                    context["mainString"] = "YES"
                    context["subString"] = "You could try and get in touch and he will get back to you. See contact links below."
                    if (end-now).minutes < 15:
                        context["subString"] = "But it's nearly over! You could try and get in touch and he will get back to you. See contact links below."
                    break
    return render_template('home.html', context=context)

if __name__ == "__main__":
    app.run()
