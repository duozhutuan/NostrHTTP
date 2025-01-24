from nostrclient.relay_pool import RelayPool
from nostrclient import bech32
from nostrclient import nip19
from nostrclient.user import User
from queue import Queue
from datetime import datetime
from .config import bridge, relayServer,searchServer
import socket
import threading

#1. set ipv4
socket.getaddrinfo = lambda *args: [(socket.AF_INET, socket.SOCK_STREAM, 6, '', (args[0], args[1]))]

#2. relay server config
relays = [bridge + relay for relay in relayServer]
search_relays = [bridge + relay for relay in searchServer]

r = RelayPool(relays)
r.connect(5)

rs = RelayPool(search_relays)
rs.connect(0)

#3. wait ...
event_queue = Queue()

def bech32encode(rawid):
    converted_bits = bech32.convertbits(rawid, 8, 5)
    return bech32.bech32_encode("note", converted_bits)

def bech32encode_nevent(rawid,author):
    return nip19.encode_bech32("nevent",{"author":author,"id":rawid})
def clear_queue():
    while not event_queue.empty():
        try:
            event_queue.get_nowait()
        except:
            break

def filter_event(event,r2=r):
    resp = []
    count = 100
    if event['limit']:
        count = event['limit']

    clear_queue()
    def handler_event(e):
        bech32id = bech32encode(bytes.fromhex(e['id']))
        e['created_at_d'] = datetime.fromtimestamp(e['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        e['bech32id'] = bech32id
        e['neventid'] = bech32encode_nevent(e['id'],e['pubkey'])
        resp.append(e)
        if len(resp) >= count:
            event_queue.put("done")
        
    subs = r2.subscribe(event)
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
    relays1 = [bridge + relay for relay in server]
    r1 = RelayPool(relays1)
    r1.connect(2)
    resp = filter_event(event,r1)
    for r2 in r1.RelayList:
        r2.off("CLOSE",r2.reconnect)
    r1 = None
    return resp

def nip19event(url,data):
    """
    if url:
        server = [url]
        relays1 = [bridge + relay for relay in server]
        r1 = RelayPool(relays1)
        r1.connect(5)
    else:
        r1 = r
    """
    if url:
        r.add_relay(bridge+url)

    result = None
    if data.startswith("note1"):
        hrp, data  = bech32.bech32_decode(data)
        eventid = bytes(bech32.convertbits(data, 5, 8)[:-1]).hex()
        result = r.fetchEvent({"ids":[eventid]})
        user = User(result['pubkey'],r1)
        profile = user.fetchProfile()

        e = result
        bech32id = bech32encode(bytes.fromhex(result['id']))
        result['created_at_d'] = datetime.fromtimestamp(e['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        result['neventid']   = bech32encode_nevent(e['id'],e['pubkey'])
        result['bech32id']   = bech32id
        result['author']     = profile.to_dict()
    elif data.startswith("nevent1"):
        data = nip19.decode_bech32(data)
        result = r.fetchEvent({"ids":[data['id']]})
        e = result
        user = User(result['pubkey'],r)
        profile = user.fetchProfile()
        bech32id = bech32encode(bytes.fromhex(result['id']))
        result['created_at_d'] = datetime.fromtimestamp(result['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        result['neventid']   = bech32encode_nevent(e['id'],e['pubkey'])
        result['bech32id']   = bech32id
        result['author']     = profile.to_dict()
        """
        author = r1.fetchEvent({
            "kinds": [0],
            "authors": [data['author']]})
        """
    else:
        return []
    if url:
        r.del_relay(bridge+url)

    return [result]

def search_event(keyword):
    filters    = {"kinds":[1,30023],"limit":100,"search":keyword}
    resp = []
    count = 100
    condition = threading.Condition()

    def handler_event(e):
        bech32id = bech32encode(bytes.fromhex(e['id']))
        e['created_at_d'] = datetime.fromtimestamp(e['created_at']).strftime("%Y-%m-%d %H:%M:%S")
        e['bech32id'] = bech32id
        e['neventid'] = bech32encode_nevent(e['id'],e['pubkey'])
        resp.append(e)
        if len(resp) >= count:
            with condition:
                condition.notify()
                            

    subs = rs.subscribe(filters)
    subs.on("EVENT",handler_event)
    with condition:
           condition.wait(timeout=5)
    return resp

