import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
ptzlog = log.getChild('relay')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'events', 'onvif_relay', log=log.getChild('config'))

import paho.mqtt.client as mqtt

from onvif import ONVIFCamera
from onvif.exceptions import ONVIFError

from onvif_ptz import OnvifPTZ
from utils import socketcontext
from alarm_packet import parse_pkt, Alarm, is_trigger_event
import datetime

setup_cmd = ( 'SetRelayOutputSettings', {
    'RelayOutputToken': config.onvif_relay.relay.token,
    'Properties': {
        'Mode': config.onvif_relay.relay.mode,
        'DelayTime': datetime.timedelta(seconds=config.onvif_relay.relay.time),
        'IdleState': config.onvif_relay.relay.idle,
    }})
alarm_cmd = ('SetRelayOutputState', {
    'RelayOutputToken': config.onvif_relay.relay.token,
    'LogicalState':'active'
    })

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_raw)

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if is_trigger_event(pkt, config.events):
        camera.devicemgmt.SetRelayOutputSettings({
            'RelayOutputToken': config.onvif_relay.relay.token,
            'Properties': {
                'Mode': config.onvif_relay.relay.mode,
                'DelayTime': datetime.timedelta(seconds=config.onvif_relay.relay.time),
                'IdleState': config.onvif_relay.relay.idle,
            }})

try:
    log.info('setting up ONVIF control')
    camera = ONVIFCamera(**config.onvif_relay.onvif)
    camera.devicemgmt.SetRelayOutputState({
        'RelayOutputToken': config.onvif_relay.relay.token,
        'LogicalState':'active'
        })

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt.server)
    
    client.loop_forever()
    
except (AssertionError, KeyError, ONVIFError):
    log.exception('error, reinit ptz')
except:
    log.exception('error')
    raise
