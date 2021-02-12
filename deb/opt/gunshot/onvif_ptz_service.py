import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('ptz')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'onvif', 'onvif_ptz', log=log.getChild('config'))

import paho.mqtt.client as mqtt
import json

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from onvif_ptz import OnvifPTZ
from utils import socketcontext


def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_alarm)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8","ignore"))
    mqlog.info("recieved message {}".format(repr(data)))

    az = data.get('az', data.get('az_raw'))
    el = data.get('el', data.get('el_raw'))

    if az is not None:
        ptzlog.info("moving to {}, {}".format(az, el))
        ptz.move(az, el, None)

log.info('setting up ONVIF control')
camera = ONVIFCamera(*config.onvif.conn)
ptz = OnvifPTZ(camera, config.onvif_ptz.limits)

log.info('connnecting to MQTT')
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(**config.mqtt.server)

client.loop_forever()
