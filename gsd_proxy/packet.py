from scapy.packet import Packet
from scapy.fields import StrFixedLenField, StrFixedLenEnumField, ByteField
import scapy.error

class AssertStringField(StrFixedLenField):
    __slots__ = ["ex"]
    def __init__(self, name, default, ex=AssertionError):
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
        
class Alarm(Packet):
    name = "Alarm "
    fields_desc=[
        AssertStringField("header", b'MD5'),
        StrFixedLenEnumField("type", b'C', length=1, enum={b'C':"gunshot", b'I':"non-gunshot"}),
        StrFixedLenField("az", b'000', length=3),
        AssertStringField("", b' '),
        StrFixedLenField("el", b'00', length=2),
        AssertStringField("", b' '),
        *(ByteField(s, 0) for s in [ # TODO verify correct order, cuz this is wack.
            "century", "day", "hour", "minute", "month", "second", "weekday", "year"]), 
        ByteField("alarm_num", 0),
        *(ByteField("mic{}_{}".format(d,s), 0) for d in range(4) for s in "wsd")
    ]

headers = {
    b'MD5': Alarm
}
def parse_pkt(data):
    return headers.get(data[:3], Packet)(data)