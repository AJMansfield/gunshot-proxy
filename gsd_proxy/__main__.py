import logging
logging.basicConfig(level=logging.INFO)

import socketserver
import socket
import threading
import queue
import collections
import time

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError
from .onvif_ptz import OnvifPTZ
from .utils import dotdict, socketcontext
from .packet import parse_pkt, Alarm

from .settings import settings
camparam = settings['camera']
server_tup = (settings['server']['host'], settings['server']['port'])
sentri_tup = (settings['sentri']['host'], settings['sentri']['port'])


cam_queue = queue.Queue() # thread safe, auto-discards when overfull
prx_queue = queue.Queue() # thread safe, auto-discards when overfull

class GSDHandler(socketserver.BaseRequestHandler):
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)
        self.log = logging.getLogger(threading.current_thread().getName()).getChild('handler')
        self.log.info("ready")
    def handle(self):
        # log = logging.getLogger('GSDHandler')
        data = self.request.recv(1024).strip()
        self.log.info(f"data={data}")

        try: cam_queue.put_nowait(data)
        except queue.Full: pass
        try: prx_queue.put_nowait(data)
        except queue.Full: pass

    def finish(self, *args, **kwargs):
        super().finish(*args, **kwargs)
        # log = logging.getLogger('GSDHandler')
        self.log.info("complete")

def cam_forever():
    log = logging.getLogger(threading.current_thread().getName())
    log.info(f'starting camera thread')
    while True:
        cam_reinit_loop(log)
        time.sleep(10)

def cam_reinit_loop(log):
    log = log.getChild('handler')
    try:
        log.info(f'setting up ONVIF control')
        camera = ONVIFCamera(**camparam['onvif'])
        limits = dotdict(camparam['limits'])
        ptz = OnvifPTZ(camera, limits)

        while True:
            cam_task_loop(ptz, log)

    except (AssertionError, KeyError, ONVIFError):
        log.exception(f'error, reinit ptz')
    except:
        log.exception(f'error')
        raise

def cam_task_loop(ptz, log):
    data = cam_queue.get()
    try:
        cam_command(ptz, data, log)
    except AssertionError:
        log.exception(f'error parsing {repr(data)}')
    except:
        log.exception(f'error processing {repr(data)}')
        raise
    finally:
        cam_queue.task_done()
        
def cam_command(ptz, data, log):
    pkt = parse_pkt(data)
    log.debug(pkt)
    if pkt.haslayer(Alarm):
        #return loop.run_in_executor(executor, ptz.move, int(pkt.az), int(pkt.el), None)
        log.info(f"moving to {int(pkt.az)}, {int(pkt.el)}")
        ptz.move(int(pkt.az), int(pkt.el), None)

def prx_forever():
    log = logging.getLogger(threading.current_thread().getName())
    log.info(f'starting proxy thread')
    while True:
        prx_reinit_loop(log)
        time.sleep(10)

def prx_reinit_loop(log):
    log = log.getChild('handler')
    try:
        log.info(f'setting up proxy socket')
        with socketcontext(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect(sentri_tup)
            while True:
                prx_task_loop(sock, log)
    except (ConnectionError, TimeoutError, OSError):
        log.exception(f'error connecting to {repr(sentri_tup)}')
    except:
        log.exception(f'error')
        raise

def prx_task_loop(sock, log):
    data = prx_queue.get()
    try:
        sent = sock.send(data)
        assert sent == len(data), "was unable to send full packet"
    except:
        log.exception(f'error sending {repr(data)}')
        raise
    finally:
        prx_queue.task_done()

with socketserver.TCPServer(server_tup, GSDHandler) as server:
    try:
        threading.Thread(target=server.serve_forever, daemon=True, name='server').start()
        threading.Thread(target=cam_forever, daemon=True, name='camera').start()
        threading.Thread(target=prx_forever, daemon=True, name='proxy').start()
    
        while True:
            time.sleep(0.5)
    finally:
        server.shutdown()