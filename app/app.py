from flask import Flask,request,render_template
from .nostr import filter_event,relay_event
from .relays import relays

app = Flask(__name__,template_folder='templates', static_folder='static')


@app.route("/")
def index():
    event = {"kinds":[1],"limit":100}
    if request.args.get("until"):
        try:
            event["until"] = int(request.args.get("until"))
        except:
            pass
    resp = filter_event(event)
    context = {"relays":relays,"data":resp}
    return render_template('index.html', **context)


@app.route("/relay/<path:url>")
def relay(url):
    event = {"kinds":[1],"limit":100}
    if request.args.get("until"):
        try:
            event["until"] = int(request.args.get("until"))
        except:
            pass
    resp = relay_event(url,event)
    context = {"relays":relays,"data":resp}
    return render_template('index.html', **context)


