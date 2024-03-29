import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')
evlog = log.getChild('event')
mqlog = log.getChild('mqtt')

import settings
config = settings.load('mqtt', 'events', log=log.getChild('config'))

import paho.mqtt.client as mqtt
import json
import datetime
import base64

from alarm_packet import parse_pkt, Alarm, source_types, alarm_types

def on_connect(client, userdata, flags, rc):
    mqlog.info("connected to broker")
    client.subscribe(config.mqtt.topics.evt_raw)

def on_message(client, userdata, msg):
    mqlog.info("recieved message {}".format(repr(msg)))

    data = {
        "time": datetime.datetime.now().isoformat(),
        "raw": base64.b64encode(msg.payload).decode('ascii'),
    }
    try:
        pkt = parse_pkt(msg.payload)
        if pkt.haslayer(Alarm):
            data.update({
                "device_type": source_types.get(pkt.device),
                "event_type": alarm_types.get(pkt.type),
                "az_raw": int(pkt.az),
                "el_raw": int(pkt.el),
                "alarm_num": pkt.alarm_num,
                "time_detector": "{x.century:02d}{x.year:02d}-{x.month:02d}-{x.day:02d}T{x.hour:02d}:{x.minute:02d}:{x.second:02d}".format(x=pkt),
                "mic_data": {alarm_dat: getattr(pkt, alarm_dat) for alarm_dat in ["mic{}_{}".format(d,s) for d in range(4) for s in "wsd"]},
            })

    except:
        evlog.exception('parse error')
        data.update({
            "error": "parse error"
        })
    
    # TODO incorporate compass data to produce north-referenced az,el
    # TODO incorporate GPS and height data to produce lat,lon

    evlog.info("processed event {}".format(repr(data)))

    json_data = json.dumps(data)

    client.publish(config.mqtt.topics.evt_all, json_data)

    if config.events.get(data.get("event_type"), False):
        client.publish(config.mqtt.topics.evt_alarm, json_data)
    


mqlog.info('connnecting to MQTT')
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(**config.mqtt.server)

client.loop_forever()
