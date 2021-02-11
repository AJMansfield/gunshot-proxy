import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
gsdlog = log.getChild('gsd')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'detector', log=log.getChild('config'))

import paho.mqtt.client as mqtt
import socket
import socketserver

class GSDHandler(socketserver.BaseRequestHandler):
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        gsdlog.info("configuring socket")
        self.request.setblocking(False)

        mqlog.info("setting up connection")

        def on_connect(client, userdata, flags, rc):
            mqlog.info("connected to broker")
            client.subscribe(config.mqtt.topics.cmd_raw)

        def on_message(client, userdata, msg):
            mqlog.info("recieved command {}".format(repr(msg)))
            gsdlog.info("sending command {}".format(repr(msg.payload)))
            self.request.sendall(msg.payload)
            # mqttlog.getChild(msg.topic.replace('/','.')).info(str(msg.payload))
        
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(**config.mqtt.server)

        log.info("ready")

    def handle(self):
        while True:
            self.client.loop()
            try:
                data = self.request.recv(1024)
                gsdlog.info("recieved event {}".format(repr(data)))
                event = self.client.publish(config.mqtt.topics.evt_raw, data)
                mqlog.info("published {}".format(repr(event)))
            except BlockingIOError:
                pass

    def finish(self, *args, **kwargs):
        super().finish(*args, **kwargs)
        log.warning("disconnected")
        self.client.disconnect()

log.info("listening on {}".format(config.detector.listen))
server = socketserver.TCPServer(socket.getaddrinfo(**config.detector.listen)[0][4], GSDHandler)
log.info("waiting for connection")
server.serve_forever()