import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
senlog = log.getChild('senseit')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'senseit_server', log=log.getChild('config'))

import paho.mqtt.client as mqtt
import socket

from net_conn import make_connection

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_raw)

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))
    senlog.info("sending event {}".format(repr(msg.payload)))
    sock.sendall(msg.payload)

log.info('setting up socket')
with make_connection(config.senseit_server.bind, config.senseit_server.conn) as sock:

    mqlog.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt.server)
    
    while True:
        client.loop()
        try:
            data = sock.recv(1024)
            if data and len(data) > 0:
                senlog.info("recieved command {}".format(repr(data)))
                event = client.publish(config.mqtt.topics.cmd_raw, data)
                mqlog.info("published {}".format(repr(event)))
        except BlockingIOError:
            pass