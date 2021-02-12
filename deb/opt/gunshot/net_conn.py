from urllib.parse import urlparse
import socket
import socketserver
import threading
import requests

def getservbyname(name, proto=None): # wrapper to adapt kwargs to *args only api
    if proto:
        return socket.getservbyname(name, proto)
    else:
        return socket.getservbyname(name)
def getservbyport(port, proto=None): # wrapper to adapt kwargs to *args only api
    if proto:
        return socket.getservbyport(port, proto)
    else:
        return socket.getservbyport(port)

def prefix_urlhost(urlish):
    if '//' not in urlish:
        return '//' + urlish
    else:
        return urlish

def extract_host(parse, default_family=0, bind=False):
    host = parse.hostname or 'localhost'

    if bind and host=='localhost':
        host = {
            0: '0.0.0.0',
            socket.AF_INET: '0.0.0.0',
            socket.AF_INET6: '::',
        }[default_family]

    try:
        host = socket.getaddrinfo(host, None, family=default_family)[0][4][0]
    except (TypeError, OSError, IndexError, socket.gaierror):
        host = socket.getaddrinfo(host, None)[0][4][0]
    
    return host

def extract_proto(parse, host='localhost', default=None):
    try: # if the scheme is specifying a protocol, like `tcp://` or `udp://`
        proto = socket.getprotobyname(parse.scheme)
    except (TypeError, OSError):
        try:
            proto = socket.getaddrinfo(host, parse.scheme, flags=socket.AI_NUMERICHOST)[0][2]
        except (TypeError, OSError):
            try:
                proto = socket.getprotobyname(default)
            except (TypeError, OSError):
                proto = default
    return proto

def extract_port(parse, host='localhost', proto=0, default=None):
    if parse.port:
        port = parse.port
    else:
        try:
            port = socket.getaddrinfo(host, parse.scheme, proto=proto, flags=socket.AI_NUMERICHOST)[0][4][1]
        except (TypeError, OSError, IndexError):
            try:
                port = getservbyname(default, prot=proto)
            except (TypeError, OSError):
                port = default
    return port

def extract_service(parse, proto):
    if parse.scheme:
        serv = parse.scheme
    else:
        serv = {
            socket.IPPROTO_TCP: 'tcp',
            socket.IPPROTO_UDP: 'udp',
        }.get(proto)
        # if no scheme, we don't want to talk anything but raw
    return serv

def decode_addr(addr, default_proto=0, default_port=0, default_family=0, bind=False):
    if addr == None:
        return None

    addr = prefix_urlhost(addr)
    parse = urlparse(addr)
    host = extract_host(parse, default_family=default_family, bind=bind)
    proto = extract_proto(parse, host=host, default=default_proto)
    port = extract_port(parse, host=host, proto=proto, default=default_port)
    serv = extract_service(parse, proto)

    return (*socket.getaddrinfo(host, port, proto=proto)[0], serv)

def decode_hostport(addr):
    addr = prefix_urlhost(addr)
    parse = urlparse(addr)
    host = parse.hostname
    port = extract_port(parse)
    return host, port

def decode_hostportuserpass(addr):
    addr = prefix_urlhost(addr)
    parse = urlparse(addr)
    host = parse.hostname
    port = extract_port(parse)
    user = parse.username
    passw= parse.password
    return host, port, user, passw

def make_connection(
        bind=None, conn=None, # bind and conn are url-ish
        bind_port=0, conn_port=0, proto=0, family=socket.AF_INET, # default ports, protocol, ipv4/6
        conn_per_message=False,
        handler=None): # handler is a socketserver.BaseRequestHandler if applicable
    
    bind_ai = decode_addr(bind, default_proto=proto, default_port=bind_port, default_family=family, bind=True) # Tuple[family, type, proto, cannonname, sockaddr, service]
    conn_ai = decode_addr(conn, default_proto=proto, default_port=conn_port, default_family=bind_ai[0]) #Tuple[family, type, proto, cannonname, sockaddr, service]

    if conn_ai and conn_ai[5] in ['http', 'https']: # use http requests API instead of sockets
        return HTTPConnection(conn)
    elif bind_ai and not conn_ai:
        return ContinuousConnection(bind_ai, conn_ai)
        #return ServerConnection(bind_ai, handler) # TODO ensure message 
    elif conn_per_message:
        return PerMessageConnection(bind_ai, conn_ai)
    else:
        return ContinuousConnection(bind_ai, conn_ai)

class ContinuousConnection:
    def __init__(self, bind_ai, conn_ai): # handler is a socketserver.BaseRequestHandler if applicable
        self.bind = bind_ai
        self.conn = conn_ai
        s = self.bind or self.conn
        self.family = s[0]
        self.stype = s[1]
        self.proto = s[2]
        self.serv = s[5]

    def __enter__(self):
        self.sock = socket.socket(self.family, self.stype, self.proto)
        if self.bind: # we want to bind a specific port
            if self.bind[4][1] != 0: # we have a specific port we want to use
                self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(self.bind[4])

        if self.conn:
            self.sock.connect(self.conn[4])
            self.supersock = None
        else:
            self.sock.listen()
            tup = self.sock.accept()
            self.sock.close()
            self.sock = tup[0]

        self.sock.setblocking(False)
        return self
        
    def __exit__(self, ex_type, ex_val, tb):
        if self.sock != None:
            self.sock.close()
            self.sock = None
    
    def send(self, msg):
        return self.sock.send(msg)
    def sendall(self, msg):
        return self.sock.sendall(msg)
    def recv(self, n):
        return self.sock.recv(n)

class PerMessageConnection:
    def __init__(self, bind_ai, conn_ai): # handler is a socketserver.BaseRequestHandler if applicable
        self.bind = bind_ai
        self.conn = conn_ai
    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_val, tb):
        pass

    def send(self, msg):
        with ContinuousConnection(self.bind, self.conn) as sock:
            return sock.send(msg)
    def sendall(self, msg):
        with ContinuousConnection(self.bind, self.conn) as sock:
            return sock.sendall(msg)
    def recv(self, n):
        with ContinuousConnection(self.bind, None) as sock:
            return sock.recv(n)

class HTTPConnection:
    def __init__(self, url): # handler is a socketserver.BaseRequestHandler if applicable
        self.url = url
    def __enter__(self):
        return self
    def __exit__(self, ex_type, ex_val, tb):
        pass
    def send(self, msg):
        requests.post(self.url, msg, timeout=1)
        return len(msg)
    def sendall(self, msg):
        requests.post(self.url, msg, timeout=1)
        return len(msg)
    def recv(self, n):
        requests.get(self.url, timeout=1).content
