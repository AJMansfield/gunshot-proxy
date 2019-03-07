import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
gsdlog = log.getChild('gsd')
mqlog = log.getChild('mqtt')

import paho.mqtt.client as mqtt
import socketserver

from settings import settings
srv_settings = settings['senseit_client']

class CalHandler(socketserver.BaseRequestHandler):
    def setup(self, *args, **kwargs):
        super().setup(*args, **kwargs)

        gsdlog.info("configuring socket")
        self.request.setblocking(False)

        mqlog.info("setting up connection")

        def on_connect(client, userdata, flags, rc):
            mqlog.info("connected to broker")
            client.subscribe("sentri/detector/event/raw")

        def on_message(client, userdata, msg):
            mqlog.info("recieved event {}".format(repr(msg)))
            gsdlog.info("sending event {}".format(repr(msg.payload)))
            self.request.sendall(msg.payload)
            # mqttlog.getChild(msg.topic.replace('/','.')).info(str(msg.payload))
        
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_message = on_message
        self.client.connect(**settings['mqtt'])

        log.info("ready")

    def handle(self):
        while True:
            self.client.loop()
            try:
                data = self.request.recv(1024)
                gsdlog.info("recieved command {}".format(repr(data)))
                event = self.client.publish("sentri/detector/command/raw", data)
                mqlog.info("sent command {}".format(repr(event)))
            except BlockingIOError:
                pass

    def finish(self, *args, **kwargs):
        super().finish(*args, **kwargs)
        log.warning("disconnected")
        self.client.disconnect()

log.info("listening on {}".format(srv_settings['listen']))
server = socketserver.TCPServer(srv_settings['listen'], CalHandler)
log.info("waiting for connection")
server.serve_forever()