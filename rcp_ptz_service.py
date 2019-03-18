import logging
logging.basicConfig(level=logging.INFO)

"""
RCP command set:
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/documents_1/rcp_commands_for_advanced_integration_package_2013-11-08.pdf
"""

log = logging.getLogger('')
ptzlog = log.getChild('ptz')
mqlog = log.getChild('mqtt')

import paho.mqtt.client as mqtt

from rcp_ptz import RCPPTZ
from utils import dotdict, socketcontext
from alarm_packet import parse_pkt, Alarm, is_trigger_event

from settings import settings
camparam = settings['rcp_ptz']

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe("sentri/detector/event/raw")

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    pkt = parse_pkt(msg.payload)
    if is_trigger_event(pkt):
        az, el = int(pkt.az), int(pkt.el)
        ptzlog.info("moving to {}, {}".format(az, el))
        ptz.move(az, el, None)

try:
    log.info('setting up RCP control')
    limits = dotdict(camparam['limits'])
    ptz = RCPPTZ(camparam['conn'], limits)

    log.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**settings['mqtt'])
    
    client.loop_forever()
    
except:
    log.exception('error')
    raise
