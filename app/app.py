from flask import Flask,request,render_template
from .nostr import filter_event,relay_event,nip19event
from .relays import relays
from .config import Home

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
    context = {"relays":relays,"data":resp,"Home":Home}
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
    context = {"relays":relays,"data":resp,"Home":Home}
    return render_template('index.html', **context)

@app.route("/notes/<data>")
def notes(data):
    url = None
    if request.args.get("r"):
        url = request.args.get("r")
    
    resp = nip19event(url,data)

    context = {"relays":relays,"data":resp,"Home":Home}
    return render_template('index.html', **context)


