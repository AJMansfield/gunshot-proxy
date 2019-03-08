from utils import translate

"""
Based on http://resource.boschsecurity.us/documents/OSRD_Protocol_Operation_Manual_enUS_9007201644423051.pdf
"""

POSITION_COMMAND = b'\x0A'

def int_to_7bit(v, length=None):
    data = b''
    while v != 0:
        data = bytes([v & 0x7F]) + data
        v = v >> 7
    if length:
        while length > len(data):
            data = b'\x00' + data
        if len(data) > length:
            raise ValueError("{} is too large to fit in {} bytes".format(v, length))
    return data

def len_cs(data):
    with_len = bytes([len(data)+1 | 0x80]) + data
    with_cs = with_len + bytes([sum(with_len) & 0x7f])
    return with_cs

def clamp(value, lower, upper):
    return sorted([value, lower, upper])[1]

def create_osrd_pt(addr, az, el):
    az = clamp(round(az), 0, 127999)
    el = clamp(round(az), 0, 31999)
    return len_cs( int_to_7bit(addr, 2) + POSITION_COMMAND + int_to_7bit(az, 3) + int_to_7bit(el, 3) )