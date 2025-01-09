from flask import Flask,request,render_template,send_from_directory
from .nostr import filter_event,relay_event,nip19event
from .relays import relays
from .config import Home
import time

app = Flask(__name__,template_folder='templates', static_folder='static')

def safe_int(args,default = 0):
    if args is None:
        return default
    try:
        return int(args)
    except:
        return default


@app.route("/")
def index():
    kind = 1
    until = int(time.time())    
    event = {"limit":100}

    ret = safe_int(request.args.get("kind"),kind)
    kind = ret
    event["kinds"] = [kind]

    ret = safe_int(request.args.get("until"),until)
    until = ret
    event['until'] = until

    resp = filter_event(event)
    context = {"relays":relays,"data":resp,"Home":Home,"kind":kind,"until":until}
    return render_template('index.html', **context)

@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, 'robots.txt')

@app.route("/relay/<path:url>")
def relay(url):
    kind = 1
    until = int(time.time())    
    event = {"limit":100}

    ret = safe_int(request.args.get("kind"),kind)
    kind = ret
    event["kinds"] = [kind]

    ret = safe_int(request.args.get("until"),until)
    until = ret
    event['until'] = until
 
    resp = relay_event(url,event)
    context = {"relays":relays,"data":resp,"Home":Home,"kind":kind,"until":until}
    return render_template('index.html', **context)

@app.route("/notes/<data>")
def notes(data):
    url = None
    if request.args.get("r"):
        url = request.args.get("r")
    
    resp = nip19event(url,data)

    context = {"relays":relays,"data":resp,"Home":Home,"notes":1}
    return render_template('index.html', **context)


