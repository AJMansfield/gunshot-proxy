from scapy.packet import Packet
from scapy.fields import StrFixedLenField, StrFixedLenEnumField, ByteField
import scapy.error


class WrongPacketType(Exception):
    pass

class AssertStringField(StrFixedLenField):
    __slots__ = ["ex"]
    def __init__(self, name, default, ex=WrongPacketType):
        super().__init__(name, default, length=len(default))
        self.ex = ex
    def getfield(self, pkt, s):
        r, v = super().getfield(pkt, s)
        if v != self.default:
            if self.ex:
                raise self.ex("invalid value {}".format(v))
            else:
                scapy.error.log_runtime.getChild('assert-field').warn("invalid value {}".format(v))
        return r, v
class AssertStrFixedLenEnumField(StrFixedLenEnumField):
    __slots__ = ["ex", "allowed"]
    def __init__(self, *args, **kwargs):
        self.ex = kwargs.get("ex", WrongPacketType)
        self.allowed = kwargs.get("allowed") or [kwargs.get('default')]
        super().__init__(*args, **kwargs)
    def getfield(self, pkt, s):
        r, v = super().getfield(pkt, s)
        if v not in self.allowed:
            if self.ex:
                raise self.ex("invalid value {}".format(v))
            else:
                scapy.error.log_runtime.getChild('assert-field').warn("invalid value {}".format(v))
        return r, v

source_types = {
    b'M': 'detector',
    b'N': 'sentri server',
}

alarm_types = {
    b'C': "gunshot",
    b'I': "non-gunshot",
# note, existence of types M,P,Q,V was only determined through reverse-engineering
# packet layout for the following alarm types is not known (although experimentally confirmed to not be the same as the first two)
    b'M': "engine alarm",
    b'P': "footstep alarm",
    b'Q': "fence alarm",
    b'V': "version", 
}

class Alarm(Packet):
    name = "Alarm "
    fields_desc=[
        AssertStrFixedLenEnumField("device", b'M', length=1, enum=source_types, allowed=b'M'), # device type field, only detector alarms are implemented currently
        AssertStringField("header", b'D5'), # no idea what these bytes mean
        AssertStrFixedLenEnumField("type", b'C', length=1, enum=alarm_types, allowed=b'CI'), # alarm type field, only gunshot and non-gunshot are implemented currently

        StrFixedLenField("az", b'000', length=3), # azimuth angle in degrees, expressed as an ASCII decimal value
        AssertStringField("", b' '),
        StrFixedLenField("el", b'00', length=2), # elevation angle in degrees, expressed as an ASCII decimal value
        AssertStringField("", b' '),

        *[ByteField(s, 0) for s in [ # TODO experimentally verify this highly unusual field ordering
            "century", "day", "hour", "minute", "month", "second", "weekday", "year"]],

        ByteField("alarm_num", 0), # increments each time the detector emits something

        *[ByteField("mic{}_{}".format(d,s), 0) for d in range(4) for s in "wsd"], # not sure what these fields actually do
    ]

packet_try_order = [
    Alarm,
    # TODO implement parsing for sentri server downstream packets and other packet types
    Packet
]
def parse_pkt(data):
    for packet in packet_try_order:
        try:
            return packet(data)
        except WrongPacketType:
            continue

def is_trigger_event(pkt, event_config):
    return pkt.haslayer(Alarm) and event_config.get(alarm_types[pkt.type], False)

