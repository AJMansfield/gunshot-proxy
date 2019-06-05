import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
senlog = log.getChild('senseit')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'senseit_server', log.getChild('config'))

import paho.mqtt.client as mqtt
import socket

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe("sentri/detector/event/raw")

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))
    senlog.info("sending event {}".format(repr(msg.payload)))
    sock.sendall(msg.payload)

try:
    senlog.info('setting up socket')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    if 'bind' in config.senseit_server:
        sock.bind(socket.getaddrinfo(**config.senseit_server.bind)[4])
    sock.connect(socket.getaddrinfo(**config.senseit_server.connect)[4])
    sock.setblocking(False)

    mqlog.info('connnecting to MQTT')
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(**config.mqtt)
    
    while True:
        client.loop()
        try:
            data = sock.recv(1024)
            senlog.info("recieved command {}".format(repr(data)))
            event = client.publish("sentri/detector/command/raw", data)
            mqlog.info("published {}".format(repr(event)))
        except BlockingIOError:
            pass
except:
    log.exception('error')
    raise
finally:
    sock.close()
