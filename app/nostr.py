from nostrclient.relay_pool import RelayPool
from queue import Queue

relayServer =  [ 
  'wss://relay.damus.io',
  'wss://strfry.iris.to',
  'wss://nos.lol',
];

hub = "wss://bridge.duozhutuan.com/";
#hub = "ws://localhost:8088/";

relays = [hub + relay for relay in relayServer]

r = RelayPool(relays)
r.connect(5)
event_queue = Queue()

def filter_event(event):
    resp = []
    count = 100
    if event['limit']:
        count = event['limit']
    def handler_event(e):
        resp.append(e)
        if len(resp) >= count:
            event_queue.put("done")
        
    subs = r.subscribe(event)
    subs.on("EVENT",handler_event)
    
    event_queue.get(timeout=2)

    subs.close()
    subs.off("EVENT",handler_event)
    return resp

def relay_event(url,event):
    server = [url]
    relays1 = [hub + relay for relay in server]
    r1 = RelayPool(relays1)
    r1.connect(2)
    resp = filter_event(event)
    for r2 in r1.RelayList:
        r2.off("CLOSE",r2.reconnect)
    return resp

