import logging
logging.basicConfig(level=logging.INFO)

import asyncio
import concurrent.futures
import pproxy
import pproxy.proto

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError
from .onvif_ptz import OnvifPTZ
from .utils import dotdict
from .packet import parse_pkt, Alarm

from .settings import settings
camparam = settings['camera']
camera = ONVIFCamera(**camparam['onvif'])
limits = dotdict(camparam['limits'])
ptz = OnvifPTZ(camera, limits)

loop = asyncio.get_event_loop()
# executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)

def command_camera(data):
    log = logging.getLogger('command')
    try:
        log.info(data)
        pkt = parse_pkt(data)
        log.debug(pkt)
        if pkt.haslayer(Alarm):
            #return loop.run_in_executor(executor, ptz.move, int(pkt.az), int(pkt.el), None)
            log.info(f"moving to {int(pkt.az)}, {int(pkt.el)}")
            ptz.move(int(pkt.az), int(pkt.el), None)
    except (AssertionError, KeyError, ONVIFError):
        log.exception(f'error processing {repr(data)}')
    except:
        log.exception(f'error processing {repr(data)}')
        raise

class SentriServer(pproxy.proto.Tunnel):
    async def channel(self, reader, writer, stat_bytes, stat_conn):
        try:
            stat_conn(1)
            while True:
                data = await reader.read_()
                if not data:
                    break
                if stat_bytes is None:
                    continue
                stat_bytes(len(data))
                writer.write(data)
                command_camera(data)
                await writer.drain()
        except Exception:
            pass
        finally:
            stat_conn(-1)
            writer.close()
pproxy.proto.MAPPINGS['sentri'] = SentriServer


server = pproxy.Server(settings['server'])
remote = pproxy.Connection(settings['conn'])
args = dict( rserver = [remote],
             verbose = logging.getLogger('pproxy').info)

handler = loop.run_until_complete(server.start_server(args))
try:
    loop.run_forever()
except KeyboardInterrupt:
    print('exit!')

handler.close()
loop.run_until_complete(handler.wait_closed())
loop.run_until_complete(loop.shutdown_asyncgens())
loop.close()