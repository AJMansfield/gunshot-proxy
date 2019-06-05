from scapy.packet import Packet, bind_layers
from scapy.fields import FlagsField, ConditionalField, ShortField, XShortField, ShortEnumField, XShortEnumField, IntField, XByteField, ByteEnumField
import scapy.error

from bicom_defs import bicom_servers, bicom_operation, bicom_ptz_objects

"""
References: 
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/protocols_1/bicom.pdf
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/documents_1/rcp_commands_for_advanced_integration_package_2013-11-08.pdf
"""

class BiCom(Packet):
    name = "BiCom "
    fields_desc=[
        FlagsField("flags", 0x80, 8, ["return_payload", "best_effort", "native_errors", "lease_time_available", "f4", "f5", "f6", "flags_available"]),

        ConditionalField(ShortField("lease_time", 0), lambda x: x.flags.lease_time_available),
        ConditionalField(IntField("lease_time_id", 0), lambda x: x.flags.lease_time_available),

        ShortEnumField("bicom_server_id", 0, bicom_servers),
    ]
    def default_payload_class(self, payload):
        return BiComCommand

class BiComCommand(Packet):
    name = "Command "
    fields_desc=[
        XShortField("object_id", 0),
        ByteEnumField("operation", 0, bicom_operation),
    ]

class BiComSet(Packet):
    name = "Set "
    fields_desc=[
        ShortField("value", 0),
    ]
    
for op in [0x03, 0x02]:
    bind_layers(BiComCommand, BiComSet, operation=op)

class PTZCommand(Packet):
    name = "PTZ "
    fields_desc=[
        XShortEnumField("object_id", 0, bicom_ptz_objects),
        ByteEnumField("operation", 0, bicom_operation),
    ]
bind_layers(BiCom, PTZCommand, bicom_server_id=6)

class PTZPosSet(Packet):
    name = "PosSet "
    fields_desc=[
        ShortField("pan", 0), # degree x 100
        ShortField("tilt", 0), # degree x 100
        ShortField("zoom", 0), # focal length x 100
        FlagsField("ignore", 0, 8, ["zoom", "tilt", "pan", "f3", "f4", "f5", "f6", "f7"]),
        XByteField("dc", 0),
    ]

for oid in [0x0a0b, 0x01d0]:
    for op in [0x03, 0x02]:
        bind_layers(PTZCommand, PTZPosSet, object_id=oid, operation=op)


for op in [0x02, 0x03]:
    bind_layers(PTZCommand, BiComSet, operation=op)