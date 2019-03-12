from utils import translate, clamp
import angles

"""
Based on http://resource.boschsecurity.us/documents/OSRD_Protocol_Operation_Manual_enUS_9007201644423051.pdf
"""

def int_to_7bit(v, length=None):
    data = b''
    if v < 0:
        raise ValueError("negative values are not supported: {}".format(v))
    while v != 0:
        data = bytes([v & 0x7F]) + data
        v = v >> 7
    if length:
        while length > len(data):
            data = b'\x00' + data
        if len(data) > length:
            raise ValueError("{} is too large to fit in {} heptets".format(v, length))
    return data

def len_cs(data):
    with_len = bytes([len(data)+1 | 0x80]) + data
    with_cs = with_len + bytes([sum(with_len) & 0x7f])
    return with_cs

def op0A(addr, pan=None, tilt=None, zoom=None):
    """PTZ command using opcode 0x0A, "position commands" """
    # TODO Fix this so it actually works.
    # There's some weird stuff with ranges not being quite correct
    POSITION_COMMAND = b'\x0A'
    IGNORE_BIT = 1 << 6

    if pan is not None:
        pan_bytes = int_to_7bit(clamp(int(translate(pan, 0, 360, 0, 2**18)), 1, 2**18-1), 3) # supposed to be 128000 counts in 360, somehow it's 256000?
    else:
        pan_bytes = bytes([IGNORE_BIT, 0, 0])
    
    if tilt is not None:
        tilt_bytes = int_to_7bit(clamp(int(translate(tilt, 0, 90, 0, 32000)), 1, 31999), 3) # 32000 counts from 0=horizontal to 31999=down
    else:
        tilt_bytes = bytes([IGNORE_BIT, 0, 0])
    
    return len_cs(addr + POSITION_COMMAND + pan_bytes + tilt_bytes)
    

def op13(addr, pan=None, tilt=None, zoom=None):
    """PTZ command using opcode 0x13, "set position" """
    POSITION_COMMAND = b'\x13'
    IGNORE_PAN = 1 << 0
    IGNORE_TILT = 1 << 1
    IGNORE_ZOOM = 1 << 2
    IGNORE_BIT = 1 << 6

    mask_byte = 0x00
    if pan is not None:
        pan_bytes = int_to_7bit(round(translate(pan, 0, 360, 0, 6266)), 2) # 6.266 radians in a circle
    else:
        pan_bytes = bytes([IGNORE_BIT, 0])
        mask_byte |= IGNORE_PAN
    
    if tilt is not None:
        tilt_bytes = int_to_7bit(round(translate(tilt, 0, 90, 3438, 1868)), 2) # OSRD defines 3.438 as horizontal and 1.868 as straight down
    else:
        tilt_bytes = bytes([IGNORE_BIT, 0])
        mask_byte |= IGNORE_TILT
    
    if zoom is not None:
        zoom_bytes = int_to_7bit(round(zoom), 2) # OSRD defines 3.438 as horizontal and 1.868 as straight down
    else:
        zoom_bytes = bytes([IGNORE_BIT, 0])
        mask_byte |= IGNORE_ZOOM
    
    return len_cs(addr + POSITION_COMMAND + bytes([mask_byte]) + pan_bytes + tilt_bytes + zoom_bytes)

class OSRDPTZ:

    def __init__(self, serial, addr, limits, op=op13):
        self.serial = serial
        self.addr = int_to_7bit(addr, 2)
        self.limits = limits
        self.op = op13

    def move(self, pan, tilt, zoom):
        if tilt is not None:
            tilt = tilt + self.limits.el_off
        if pan is not None:
            pan = pan + self.limits.az_off
            pan, tilt = angles.normalize_sphere(pan, tilt)
            pan = angles.normalize(pan, 0, 360)
        if zoom is not None:
            zoom = zoom + self.limits.z_off

        self.serial.write(self.op(self.addr, pan=pan, tilt=tilt, zoom=zoom))
		