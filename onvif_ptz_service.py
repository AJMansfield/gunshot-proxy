import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('ptz')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'events', 'onvif_ptz', log=log.getChild('config'))

import paho.mqtt.client as mqtt

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from onvif_ptz import OnvifPTZ
from utils import socketcontext
from alarm_packet import parse_pkt, Alarm, is_trigger_event


def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe("sentri/detector/event/raw")

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if is_trigger_event(pkt, config.events):
        az, el = int(pkt.az), int(pkt.el)
        ptzlog.info("moving to {}, {}".format(az, el))
        ptz.move(az, el, None)

try:
    log.info('setting up ONVIF control')
    camera = ONVIFCamera(**config.onvif_ptz.onvif)
    ptz = OnvifPTZ(camera, config.onvif_ptz.limits)

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt)
    
    client.loop_forever()
    
except (AssertionError, KeyError, ONVIFError):
    log.exception('error, reinit ptz')
except:
    log.exception('error')
    raise
