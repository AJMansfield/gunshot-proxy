import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('relay')
mqlog = log.getChild('mqtt')

import paho.mqtt.client as mqtt

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from onvif_ptz import OnvifPTZ
from utils import dotdict, socketcontext
from alarm_packet import parse_pkt, Alarm

from settings import settings
camparam = settings['onvif_relay']

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe("sentri/detector/event/raw")

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if pkt.haslayer(Alarm):
        for cmd, params in camparam['alarm']: # issue all of the configured devmgmt commands
            getattr(camera.devicemgmt, cmd)(params)

try:
    log.info('setting up ONVIF control')
    camera = ONVIFCamera(**camparam['onvif'])

    for cmd, params in camparam['setup']: # issue all of the configured devmgmt commands
        getattr(camera.devicemgmt, cmd)(params)

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**settings['mqtt'])
    
    client.loop_forever()
    
except (AssertionError, KeyError, ONVIFError):
    log.exception('error, reinit ptz')
except:
    log.exception('error')
    raise
