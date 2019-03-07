import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('ptz')
mqlog = log.getChild('mqtt')

import paho.mqtt.client as mqtt

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from gsd_proxy.onvif_ptz import OnvifPTZ
from gsd_proxy.utils import dotdict, socketcontext
from gsd_proxy.packet import parse_pkt, Alarm

from gsd_proxy.settings import settings
camparam = settings['camera']

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe("sentri/detector/event/raw")

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if pkt.haslayer(Alarm):
        az, el = int(pkt.az), int(pkt.el)
        ptzlog.info("moving to {}, {}".format(az, el))
        ptz.move(az, el, None)

try:
    log.info('setting up ONVIF control')
    camera = ONVIFCamera(**camparam['onvif'])
    limits = dotdict(camparam['limits'])
    ptz = OnvifPTZ(camera, limits)

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("10.0.2.4")
    client.loop_forever()
    
except (AssertionError, KeyError, ONVIFError):
    log.exception('error, reinit ptz')
except:
    log.exception('error')
    raise
