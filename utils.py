
def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def clamp(value, lower, upper):
    return sorted([value, lower, upper])[1]

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    
import socket
from contextlib import contextmanager

@contextmanager
def socketcontext(*args, **kw):
    s = socket.socket(*args, **kw)
    try:
        yield s
    finally:
        s.close()
