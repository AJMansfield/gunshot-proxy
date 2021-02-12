from urllib.parse import urlparse
import socket
import socketserver

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

def get_scheme_port(scheme):
    socket.getservbyname(scheme)

def decode_addr(addr, default_proto=0, default_port=0, default_family=0, bind=False):
    if addr == None:
        return None
    
    if '//' not in addr:
        addr = '//' + addr # add slashes so it doesn't interpret it as a path
    
    parse = urlparse(addr)

    host = parse.hostname or 'localhost'

    if bind and host=='localhost':
        host = {
            socket.AF_INET: '0.0.0.0',
            socket.AF_INET6: '::',
        }[default_family]

    try:
        host = socket.getaddrinfo(host, None, family=default_family)[0][4][0]
    except (TypeError, OSError, IndexError, socket.gaierror):
        host = socket.getaddrinfo(host, None)[0][4][0]

    try: # if the scheme is specifying a protocol, like `tcp://` or `udp://`
        proto = socket.getprotobyname(parse.scheme)
    except (TypeError, OSError):
        try:
            proto = socket.getaddrinfo(host, parse.scheme, flags=socket.AI_NUMERICHOST)[0][2]
        except (TypeError, OSError):
            try:
                proto = socket.getprotobyname(default_proto)
            except (TypeError, OSError):
                proto = default_proto
    
    if parse.port:
        port = parse.port
    else:
        try:
            port = socket.getaddrinfo(host, parse.scheme, proto=proto, flags=socket.AI_NUMERICHOST)[0][4][1]
        except (TypeError, OSError, IndexError):
            try:
                port = getservbyname(default_proto, prot=proto)
            except (TypeError, OSError):
                port = default_port
    
    if parse.scheme:
        serv = parse.scheme
    else:
        serv = {
            socket.IPPROTO_TCP: 'tcp',
            socket.IPPROTO_UDP: 'udp',
        }.get(proto)
        # if no scheme, we don't want to talk anything but raw

    return (*socket.getaddrinfo(host, port, proto=proto)[0], serv)

def make_connection(
        bind=None, conn=None, # bind and conn are url-ish
        bind_port=0, conn_port=0, proto=0, family=socket.AF_INET, # default ports, protocol, ipv4/6
        conn_per_message=True,
        handler=None): # handler is a socketserver.BaseRequestHandler if applicable
    
    bind_ai = decode_addr(bind, default_proto=proto, default_port=bind_port, default_family=family, bind=True) # Tuple[family, type, proto, cannonname, sockaddr, service]
    conn_ai = decode_addr(conn, default_proto=proto, default_port=conn_port, default_family=bind_ai[0]) #Tuple[family, type, proto, cannonname, sockaddr, service]

    
    if conn_ai[5] in ['http', 'https']: # use http requests API instead of sockets
        return RequestsConnection(conn)
    elif self.bind and not self.conn:
        return ServerConnection(bind_ai)
    elif conn_per_message:
        return ConnPerMessageConnection(bind_ai, conn_ai)
    else:
        return ContinuousConnection(bind_ai, conn_ai)
class Connection:
    def __init__(self, bind_ai, conn_ai
            bind=None, conn=None, # bind and conn are url-ish
            bind_port=0, conn_port=0, proto=0, family=socket.AF_INET, # default ports, protocol, ipv4/6
            conn_per_message=True,
            handler=None): # handler is a socketserver.BaseRequestHandler if applicable
        
        self.bind = decode_addr(bind, default_proto=proto, default_port=bind_port, default_family=family, bind=True) # Tuple[family, type, proto, cannonname, sockaddr, service]
        self.conn = decode_addr(conn, default_proto=proto, default_port=conn_port, default_family=self.bind[0]) #Tuple[family, type, proto, cannonname, sockaddr, service]

        if self.conn[5] in ['http', 'https']: # use http requests API instead of sockets
            self.mode = 'requests'
            self.url = conn
        elif self.bind and not self.conn:
            self.mode = 'server'
        else:
            self.mode = 'client'

            s = self.conn or self.bind
            self.family = s[0]
            self.stype = s[1]
            self.proto = s[2]
            self.serv = s[5]

            self.handler = handler

            self.conn_per_message = True

        assert self.bind[0] == self.connect[0], 'must be same address family'
        assert self.bind[1] == self.connect[1], 'must be same socket type'
        assert self.bind[2] == self.connect[2], 'must be same IP protocol'

    def __enter__(self):
        if self.mode == 'requests':
            pass
        elif self.mode == 'server':
            self.sockserver = {
                'tcp': socketserver.TCPServer,
                'udp': socketserver.UDPServer,
                # TODO add http server options
            }[self.bind[5]](self.bind[4], self.handler)
        elif self.mode == 'client':
            if not self.conn_per_message:
                self._socket_open()

        return self
        
    def __exit__(self, ex_type, ex_val, tb):
        if self.requests:
            pass
        if self.sock:
            self._socket_close()
        if self.sockserver:
            self.sockserver.close()
    
    def _socket_open(self):
        self.sock = socket.socket(self.family, self.stype, self.proto)
        if self.bind: # we want to bind a specific port
            if self.bind[4][2] != 0: # we have a specific port we want to use
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.bind[4])
        sock.connect(self.conn[4])
    
    def _socket_close(self):
        self.sock.close()
        self.sock = None
    
    def send(self, msg):
        try:
            if self.conn_per_message:
                self._socket_open()
            return self.socket.send(msg)
        finally:
            if self.conn_per_message:
                self._socket_close()

                
class Connection:
    def __init__(self, bind_ai, conn_ai
            bind=None, conn=None, # bind and conn are url-ish
            bind_port=0, conn_port=0, proto=0, family=socket.AF_INET, # default ports, protocol, ipv4/6
            conn_per_message=True,
            handler=None): # handler is a socketserver.BaseRequestHandler if applicable
        
        self.bind = decode_addr(bind, default_proto=proto, default_port=bind_port, default_family=family, bind=True) # Tuple[family, type, proto, cannonname, sockaddr, service]
        self.conn = decode_addr(conn, default_proto=proto, default_port=conn_port, default_family=self.bind[0]) #Tuple[family, type, proto, cannonname, sockaddr, service]

        if self.conn[5] in ['http', 'https']: # use http requests API instead of sockets
            self.mode = 'requests'
            self.url = conn
        elif self.bind and not self.conn:
            self.mode = 'server'
        else:
            self.mode = 'client'

            s = self.conn or self.bind
            self.family = s[0]
            self.stype = s[1]
            self.proto = s[2]
            self.serv = s[5]

            self.handler = handler

            self.conn_per_message = True

        assert self.bind[0] == self.connect[0], 'must be same address family'
        assert self.bind[1] == self.connect[1], 'must be same socket type'
        assert self.bind[2] == self.connect[2], 'must be same IP protocol'

    def __enter__(self):
        if self.mode == 'requests':
            pass
        elif self.mode == 'server':
            self.sockserver = {
                'tcp': socketserver.TCPServer,
                'udp': socketserver.UDPServer,
                # TODO add http server options
            }[self.bind[5]](self.bind[4], self.handler)
        elif self.mode == 'client':
            if not self.conn_per_message:
                self._socket_open()

        return self
        
    def __exit__(self, ex_type, ex_val, tb):
        if self.requests:
            pass
        if self.sock:
            self._socket_close()
        if self.sockserver:
            self.sockserver.close()
    
    def _socket_open(self):
        self.sock = socket.socket(self.family, self.stype, self.proto)
        if self.bind: # we want to bind a specific port
            if self.bind[4][2] != 0: # we have a specific port we want to use
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(self.bind[4])
        sock.connect(self.conn[4])
    
    def _socket_close(self):
        self.sock.close()
        self.sock = None
    
    def send(self, msg):
        try:
            if self.conn_per_message:
                self._socket_open()
            return self.socket.send(msg)
        finally:
            if self.conn_per_message:
                self._socket_close()






