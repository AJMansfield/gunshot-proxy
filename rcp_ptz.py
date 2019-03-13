from bicom_packet import BiCom, PTZCommand, PTZPosSet
from utils import translate, clamp
import angles
import requests
from binascii import b2a_hex

# http://10.0.2.5/rcp.xml?command=0x09A5&type=P_OCTET&direction=WRITE&num=1&payload=0x
class RCPPTZ:

    def __init__(self, conn, limits):
        """
        conn is a dict like this:
        {
            'url': 'http://10.0.2.5/rcp.xml',
            'auth': ('user', 'pass'),
        }
        """
        self.conn = conn
        self.limits = limits

    def move(self, pan, tilt, zoom):
        if tilt is not None:
            tilt = tilt + self.limits.el_off
        if pan is not None:
            pan = pan + self.limits.az_off
            pan = pan * {True:1, False:-1}[self.limits.az_flip]
            pan, tilt = angles.normalize_sphere(pan, tilt)
            pan = angles.normalize(pan, 0, 360)
        if zoom is not None:
            zoom = zoom + self.limits.z_off
        
        pkt = BiCom()/PTZCommand(object_id='PTZPosMoveStatus')/PTZPosSet()
        if pan is None: pkt.ignore.pan = True
        else: pkt.pan = round(pan*100)
        if tilt is None: pkt.ignore.tilt = True
        else: pkt.tilt = round(translate(tilt,0,90,197,107)*100)
        if zoom is None: pkt.ignore.zoom = True
        else: pkt.zoom = round(zoom)

        # return pkt
        
        requests.get(**self.conn, params=dict(
            command = 0x09A5,
            type = 'P_OCTET',
            direction = 'WRITE',
            num = 1,
            payload = '0x' + bytes(pkt).hex(),
        ))
