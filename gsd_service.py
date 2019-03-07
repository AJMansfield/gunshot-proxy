import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
gsdlog = log.getChild('gsd')
mqlog = log.getChild('mqtt')

import paho.mqtt.client as mqtt
import socketserver

from settings import settings
local_tup = (settings['gunshot']['local']['host'], settings['gunshot']['local']['port'])
remote_tup = (settings['gunshot']['remote']['host'], settings['gunshot']['remote']['port'])

class GSDHandler(socketserver.BaseRequestHandler):
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        gsdlog.info("configuring socket")
        self.request.setblocking(False)

        mqlog.info("setting up connection")

        def on_connect(client, userdata, flags, rc):
            mqlog.info("connected to broker")
            client.subscribe("sentri/detector/command/raw")

        def on_message(client, userdata, msg):
            mqlog.info("recieved command {}".format(repr(msg)))
            gsdlog.info("sending command {}".format(repr(msg.payload)))
            self.request.sendall(msg.payload)
            # mqttlog.getChild(msg.topic.replace('/','.')).info(str(msg.payload))
        
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect("10.0.2.4")

        log.info("ready")

    def handle(self):
        while True:
            self.client.loop()
            try:
                data = self.request.recv(1024)
                gsdlog.info("recieved event {}".format(repr(data)))
                event = self.client.publish("sentri/detector/event/raw", data)
                mqlog.info("published {}".format(repr(event)))
            except BlockingIOError:
                pass

    def finish(self, *args, **kwargs):
        super().finish(*args, **kwargs)
        log.warning("disconnected")
        self.client.disconnect()

log.info("listening on {}".format(local_tup))
server = socketserver.TCPServer(local_tup, GSDHandler)
log.info("waiting for connection")
server.serve_forever()