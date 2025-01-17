from flask import Flask,request,render_template,send_from_directory
from .nostr import filter_event,relay_event,nip19event,search_event
from .relays import relays
from .config import Home
import time

app = Flask(__name__,template_folder='templates', static_folder='static')

def get_filter(event,until=None,since=None):
    time_filter = {'type':None,"val":None}
    if until:
        event['until'] = until
        time_filter['type'] = "until"
        time_filter['val']  =  until
    if since:
        event['since'] = since
        time_filter['type'] = "since"
        time_filter['val']  =  since

    return time_filter

@app.route("/")
def index():
    kind = 1
    until = int(time.time())    
    event = {"limit":100}

    ret = request.args.get("kind",type=int)
    if ret:
        kind = ret

    event["kinds"] = [kind]

    time_filter = {}
    until = request.args.get("until",type=int)
    since = request.args.get("since",type=int)
    time_filter = get_filter(event,until,since)

    resp = filter_event(event)
    context = {"relays":relays,"data":resp,"Home":Home,"kind":kind,"time_filter":time_filter}
    return render_template('index.html', **context)

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route("/relay/<path:url>")
def relay(url):
    kind = 1
    until = int(time.time())    
    event = {"limit":100}

    ret = request.args.get("kind",type=int)
    if ret:
        kind = ret

    event["kinds"] = [kind]

    time_filter = {}
    until = request.args.get("until",type=int)
    since = request.args.get("since",type=int)
    time_filter = get_filter(event,until,since)

 
    resp = relay_event(url,event)
    context = {"relays":relays,"data":resp,"Home":Home,"kind":kind,"time_filter":time_filter}
    return render_template('index.html', **context)

@app.route("/notes/<data>")
def notes(data):
    url = None
    if request.args.get("r"):
        url = request.args.get("r")
    
    resp = nip19event(url,data)

    context = {"relays":relays,"data":resp,"Home":Home,"notes":1}
    return render_template('index.html', **context)


@app.route("/search")
def search():
    keyword = request.args.get("q")
    resp = search_event (keyword)
    
    context = {"relays":relays,"data":resp,"Home":Home}
    return render_template('index.html', **context)
