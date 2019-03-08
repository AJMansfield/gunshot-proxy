
"""
Commands from:
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/documents_1/rcp_commands_for_advanced_integration_package_2013-11-08.pdf

Also need to implement BiCom:
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/protocols_1/bicom.pdf
"""

"""
payload: 
80 (flags)
0006 (bicom ptz server)
one of:
    01d0 (PTZPosMoveStatus)
    0112 (Position.Pan)
    0113 (Position.Tilt)
    0114 (Position.ZoomTicks)
02 (operation = set)

for Position.pan, tilt, or zoom
    4-bytes pan in rads * 10000
    4-bytes tilt in rads * 10000
    4-bytes zoom in ticks from 0 to 255

for PTZPosMoveStatus or AutoTracker.AT
    2-bytes pan in degree * 100
    2-bytes tilt in degree * 100
    2-bytes zoom in focal length * 100
    1-byte ignore mask?
    1-byte don't care
    1-byte CRC
"""