import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('relay')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'onvif', 'onvif_relay', log=log.getChild('config'))

import paho.mqtt.client as mqtt

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from onvif_ptz import OnvifPTZ
from utils import socketcontext
from alarm_packet import parse_pkt, Alarm, is_trigger_event
import datetime

def get_relay_token(devmgmt):
    if config.onvif_relay.relay_type == "token":
        return config.onvif_relay.relay_id
    elif config.onvif_relay.relay_type == "number":
        index = int(config.onvif_relay.relay_id)
        relay = devmgmt.GetRelayOutputs()[index-1]
        token = relay['token']
        ptzlog.info("relay #{} has token {}".format(index, repr(token)))
        return token
    else:
        raise NotImplementedError()

def do_setup(devmgmt):
    ptzlog.info("setting up relay")
    devmgmt.SetRelayOutputSettings({
        'RelayOutputToken': get_relay_token(devmgmt),
        'Properties': {
            'Mode': config.onvif_relay.relay.mode,
            'DelayTime': datetime.timedelta(seconds=config.onvif_relay.relay.time),
            'IdleState': config.onvif_relay.relay.idle,
        }})

def do_alarm(devmgmt):
    ptzlog.info("triggering relay")
    devmgmt.SetRelayOutputState({
        'RelayOutputToken': get_relay_token(devmgmt),
        'LogicalState':'active'
        })

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_alarm)

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))
    do_alarm(camera.devicemgmt)

log.info('setting up ONVIF control')
camera = ONVIFCamera(**config.onvif)
do_setup(camera.devicemgmt)

log.info('connnecting to MQTT')
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(**config.mqtt.server)

client.loop_forever()
