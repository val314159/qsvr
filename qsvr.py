'''
Queue Server
'''
from gevent import sleep,monkey; monkey.patch_all()
from gevent.queue import Queue,Empty
from os import environ as E
import os,sys,bottle,leveldb,json,time
from cors import add_headers

Q,QM,RemotePortToQ=Queue(),{},{}

def remote_port(): return bottle.request.environ['REMOTE_PORT']

def close_connect():
    print "XX CLOSE CONNECT", remote_port()
    q = RemotePortToQ.pop(remote_port())
    print "QAZ close X zzzzz XXX", remote_port(), id(q)
    # clean up
    del QM[str(id(q))]
    return True

# monkey patch it!
import gevent.pywsgi
_old_sendall = gevent.pywsgi.WSGIHandler._sendall
def _new_sendall(*a,**kw):
    try:    return _old_sendall(*a,**kw)
    except: return close_connect()
gevent.pywsgi.WSGIHandler._sendall = _new_sendall

def pushseq(_,x): _.append(x); return x
def DB(_=[]): return(_[0] if _ else pushseq( _, leveldb.LevelDB('.q') ))
def MsgIter(ch,k0,kn): return DB().RangeIter(ch+'.'+k0,ch+'.'+kn)
def _put_msg(channel,msg):
    DB().Put('%s.%g' % (channel,time.time()), msg) ; return msg

@bottle.get('/since/<channel>/<when>')
def since(channel,when):
    return dict(results=[ (k,DB().Get(k)) for k,v in MsgIter(ch,'',since)])

@bottle.get('/zap/<channel>/<until>')
def zap(channel,until):
    return dict(len=len([DB().Delete(k) for k,v in MsgIter(ch,until,'~')]))

@bottle.get('/')
@bottle.get('/watch')
def watch():return open('watch.html')

@bottle.get('/send/<to_whom>/<event>/<data>')
def send(**kw):
    _put_msg('*',json.dumps(kw))
    QM[ kw.pop('to_whom') ].put(kw)
    return '{}'

@bottle.get('/send_all/<event>/<data>')
def send_all(**kw):
    _put_msg('*',json.dumps(kw))
    for k,q in QM.iteritems(): q.put(kw)
    return dict(len=len(QM))

@bottle.get('/who')
def who(): return dict(results=QM.keys())

@bottle.get('/stream')
def stream2():
    add_headers(bottle.response)
    q=Queue()
    myid = str(id(q))
    QM[myid] = q
    RemotePortToQ[remote_port()] = q
    print "QAZ open X b XXX", remote_port(), id(q)
    bottle.response.content_type  = 'text/event-stream'
    bottle.response.cache_control = 'no-cache'
    # Set client-side auto-reconnect timeout, ms.
    yield 'retry: 100\n\ndata: hello '+myid+'\n\n'
    while 1:
        arr = []
        data = q.get()
        if 'id'    in data:  arr.append('id: %s' % data['id'])
        if 'event' in data:  arr.append('event: %s' % data['event'])
        dat = data['data']
        if type(dat)!=list:  arr.append('data: '+json.dumps(dat))
        else:
            for x in dat:    arr.append('data: '+json.dumps(x))
            pass
        arr.append('\n')
        yield '\n'.join(arr)

if __name__=='__main__':bottle.run(server='gevent',port=E['PORT'],debug=True)
