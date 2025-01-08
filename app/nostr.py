from nostrclient.relay_pool import RelayPool
from nostrclient import bech32
from nostrclient import nip19
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

def bech32encode(rawid):
    converted_bits = bech32.convertbits(rawid, 8, 5)
    return bech32.bech32_encode("note", converted_bits, bech32.Encoding.BECH32)

def clear_queue():
    while not event_queue.empty():
        try:
            event_queue.get_nowait()
        except:
            break

def filter_event(event):
    resp = []
    count = 100
    if event['limit']:
        count = event['limit']

    clear_queue()
    def handler_event(e):
        bech32id = bech32encode(bytes.fromhex(e['id']))
        e['bech32id'] = bech32id
        resp.append(e)
        if len(resp) >= count:
            event_queue.put("done")
        
    subs = r.subscribe(event)
    subs.on("EVENT",handler_event)
    try:
        event_queue.get(timeout=10)
    except:
        pass

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

def nip19event(url,data):
    if url:
        server = [url]
        relays1 = [hub + relay for relay in server]
        r1 = RelayPool(relays1)
        r1.connect(2)
    else:
        r1 = r

    result = None
    if data.startswith("note1"):
        hrp, data  = bech32.bech32_decode(data)
        eventid = bytes(bech32.convertbits(data, 5, 8)[:-1]).hex()
        result = r1.fetchEvent({"ids":[eventid]})
        result
    elif data.startswith("nevent1"):
        data = nip19.decode_bech32(data)
        result = r1.fetchEvent({"ids":[data['id']]})
        """
        author = r1.fetchEvent({
            "kinds": [0],
            "authors": [data['author']]})
        """
    else:
        return []
    if url:
        r1.close()

    return [result]
