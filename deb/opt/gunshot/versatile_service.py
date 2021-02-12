# Versatile Packet Output Service
# listens to event data and outputs template data to any desired destination based on it

import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
verlog = log.getChild('versatile')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'versatile', log=log.getChild('config'))

import paho.mqtt.client as mqtt
import json
import socket

from utils import DotDict

from string import Formatter
class SafeFormatter(Formatter):
        def get_field(self, field_name, args, kwargs):
            # TODO sanitize aggressively (but we need to support dotted access)
            return super().get_field(field_name,args,kwargs)

form = SafeFormatter()


def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_all)

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8","ignore"))
    mqlog.info("recieved message {}".format(repr(data)))
    output = form.format(config.versatile.template.str, evt=DotDict(data))
    verlog.info("sending packet {}".format(repr(output)))
    sock.send(output.encode("utf-8"))

try:
    verlog.info('setting up socket')

    if config.versatile.protocol == "udp":
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(socket.getaddrinfo(**config.versatile.bind)[0][4])
        sock.connect(socket.getaddrinfo(**config.versatile.connect)[0][4])
        sock.setblocking(False)
    elif config.versatile.protocol == "tcp_client":
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(socket.getaddrinfo(**config.versatile.bind)[0][4])
        sock.connect(socket.getaddrinfo(**config.versatile.connect)[0][4])
        sock.setblocking(False)
    elif config.versatile.protocol == "tcp_server":
        raise NotImplementedError()
    else:
        raise NotImplementedError()

    mqlog.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt.server)
    
    client.loop_forever()
except:
    log.exception('error')
    raise
finally:
    sock.close()
