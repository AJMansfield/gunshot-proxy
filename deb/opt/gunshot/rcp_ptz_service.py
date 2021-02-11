import logging
logging.basicConfig(level=logging.INFO)

"""
RCP command set:
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/documents_1/rcp_commands_for_advanced_integration_package_2013-11-08.pdf
"""

log = logging.getLogger('')
ptzlog = log.getChild('ptz')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'events', 'rcp_ptz', log=log.getChild('config'))

import paho.mqtt.client as mqtt

from rcp_ptz import RCPPTZ
from utils import socketcontext
from alarm_packet import parse_pkt, Alarm, is_trigger_event

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_raw)

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if is_trigger_event(pkt, config.events):
        az, el = int(pkt.az), int(pkt.el)
        ptzlog.info("moving to {}, {}".format(az, el))
        ptz.move(az, el, None)

try:
    log.info('setting up RCP control')
    ptz = RCPPTZ(config.rcp_ptz.url, config.rcp_ptz.limits)

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt.server)
    
    client.loop_forever()
    
except:
    log.exception('error')
    raise
