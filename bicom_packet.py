from scapy.packet import Packet, bind_layers
from scapy.fields import FlagsField, ConditionalField, ShortField, XShortField, ShortEnumField, XShortEnumField, IntField, XByteField, ByteEnumField
import scapy.error


"""
References: 
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/protocols_1/bicom.pdf
https://st-tpp.resource.bosch.com/media/technology_partner_programm/10_public/downloads_1/video_8/documents_1/rcp_commands_for_advanced_integration_package_2013-11-08.pdf
"""


bicom_servers = {
    2: "device",
    4: "camera",
    6: "ptz",
    8: "ca",
    9: "ca_broadcast",
    10: "io",
    11: "io_broadcast",
    12: "vca",
    16: "intern",
    18: "factory",
}
bicom_operation = {
    0x01: 'GET',
    0x02: 'SET',
    0x03: 'SET_GET',
    0x04: 'INC',
    0x05: 'INC_GET',
    0x06: 'DEC',
    0x07: 'DEC_GET',
    0x08: 'SET_DFLT',
    0x09: 'SET_GET_DFLT',
}

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

bicom_ptz_objects = {
    0x0100: 'AutoPanScan',
    0x0101: 'AutoPanScanMode',
    0x0102: 'Speed',
    0x0103: 'RightLimit',
    0x0104: 'LeftLimit',
    0x0105: 'TourPlaybackMode',
    0x0110: 'Position',
    0x0111: 'AutoPivot',
    0x0112: 'Pan',
    0x0113: 'Tilt',
    0x0114: 'ZoomTicks',
    0x0115: 'ZoomFocalLength',
    0x0116: 'FixedSpeedControlSpeed',
    0x0119: 'AutoReport',
    0x011A: 'Orientation',
    0x011B: 'PanLeftLimit',
    0x011C: 'PanRightLimit',
    0x011D: 'TiltUpLimit',
    0x011E: 'TiltDownLimit',
    0x011F: 'AdjustableTiltLimitMode',
    0x0120: 'Zoom',
    0x0121: 'MaxSpeed',
    0x0122: 'Polarity',
    0x0125: 'WideAngleFocalLengthX10',
    0x0126: 'ZoomLens',
    0x0127: 'Propotion',
    0x0128: 'DigitalZoomEvent',
    0x0129: 'OpticalZoomLimit',
    0x0130: 'PrePositions',
    0x0131: 'PrePositionsTourPeriod',
    0x0132: 'PrePositionsMaxNumber',
    0x0133: 'PrePositionsTitleLength',
    0x0134: 'PrePositionsTour',
    0x0135: 'PrePositionsFreezeFrame',
    0x0136: 'PrePositionsSceneMenuState',
    0x0140: 'InactivityReturn',
    0x0141: 'Period',
    0x0150: 'Home',
    0x0160: 'TourA',
    0x0161: 'TourASize',
    0x0162: 'TourAStartingPosition',
    0x0163: 'TourARecordPlayBackNoAuxFlag',
    0x0170: 'TourB',
    0x0171: 'TourBSize',
    0x0172: 'TourBStartingPosition',
    0x0173: 'TourBRecordPlayBackNoAuxFlag',
    0x0180: 'PrePositionsCustom',
    0x0181: 'PrePositionsCustomTourPeriod',
    0x0182: 'PrePositionsCustomMaxNumber',
    0x0183: 'PrePositionsCustomTitleLength',
    0x0184: 'PrePositionsCustomTour',
    0x0185: 'PrePositionsCustomSlot1',
    0x0186: 'PrePositionsCustomSlot2',
    0x0190: 'ProportionalSpeedStatus',
    0x01A0: 'PositionCoordinate',
    0x01A1: 'PanCoordinate',
    0x01A2: 'TiltCoordinate',
    # 0x01B0: 'PanMotorProperties',
    0x01B0: 'PanCurrent',
    0x01B1: 'PanVelocity',
    0x01B2: 'PanPWM',
    0x01B3: 'PanCurrentProperties',
    0x01B4: 'PanDesiredHoldingCurrent',
    # 0x01C0: 'TiltMotorProperties',
    0x01C0: 'TiltCurrent',
    0x01C1: 'TiltVelocity',
    0x01C2: 'TiltPWM',
    0x01C3: 'TiltCurrentProperties',
    0x01C4: 'TiltDesiredHoldingCurrent',
    0x01D0: 'PTZPosMoveStatus',
    0x01E0: 'PTZMotorRequest',
    0x01E1: 'PTZMotorStatus',
    0x0A00: 'AutoTracker',
    0x0A01: 'Version',
    0x0A02: 'CameraHeight',
    0x0A03: 'Communications',
    0x0A04: 'Status',
    0x0A05: 'Timeout',
    0x0A06: 'TimeoutPeriod',
    0x0A07: 'AutoTrackerMode',
    0x0A08: 'AutoPivotStatus',
    0x0A09: 'TrackingStatus',
    0x0A0A: 'PTZ',
    0x0A0B: 'AT',
    0x0A0C: 'NightZoomThreshold',
    0x0A0D: 'NoMotionZoomTimeOut',
    0x0A10: 'Logging',
    0x0A11: 'TimeOnPan',
    0x0A12: 'TimeOnTilt',
    0x0A13: 'PowerOns',
    0x0A14: 'OperationHours',
    0x0A15: 'TotalPanDegrees',
    0x0A16: 'TotalTiltDegress',
    0x0A20: 'Temperature',
    0x0A21: 'TemperatureCurrentHousing',
    0x0A22: 'TemperatureCurrentBody',
    0x0A23: 'TemperatureCurrentMotor',
    0x0A24: 'TemperatureCurrentBase',
    0x0A25: 'MinimumHousing',
    0x0A26: 'MinimumBody',
    0x0A27: 'MinimumMotor',
    0x0A28: 'MinimumBase',
    0x0A29: 'MaximumHousing',
    0x0A2A: 'MaximumBody',
    0x0A2B: 'MaximumMotor',
    0x0A2C: 'MaximumBase',
    0x0A30: 'ProportionalSpeedMode',
    0x0A31: 'ProportionalSpeedPercent',
    0x0A40: 'MaskedVideo',
    0x2000: 'PrePosition1',
    0x2001: 'PrePosition1Enable',
    0x2002: 'PrePosition1Title',
    0x2003: 'PrePosition1PanPosition',
    0x2004: 'PrePosition1TiltPosition',
    0x2005: 'PrePosition1ZoomPosition',
    0x2006: 'PrePosition1GainSetting',
    0x2007: 'PrePosition1SceneDeleted',
    0x2008: 'PrePosition1BLC',
    0x2009: 'PrePosition1FocusMode',
    0x200A: 'PrePosition1ManualIris',
    0x200B: 'PrePosition1Tour',
    0x200C: 'PrePosition1VCAMode',
    0x200D: 'PrePosition1ROI',
    0x200E: 'PrePosition1FocusPosition',
    0x200F: 'PrePosition1MaxGain',
    0x2010: 'PrePosition2',
    0x2FF0: 'PrePosition256',
    0x3000: 'Sector1',
    0x3001: 'Sector1Mask',
    0x3002: 'Sector1Title',
    0x3003: 'Sector1VisibleLightInhibit',
    0x3010: 'Sector2',
    0x37F0: 'Sector128',
    0x3800: 'PrivacyMask1',
    0x3801: 'PrivacyMask1Enable',
    0x3802: 'PrivacyMask1PanPosition',
    0x3803: 'PrivacyMask1TiltPosition',
    0x3804: 'PrivacyMask1ZoomPosition',
    0x3805: 'PrivacyMask1Height',
    0x3806: 'PrivacyMask1Width',
    0x3807: 'PrivacyMask1PanPositionWideAngle',
    0x3808: 'PrivacyMask1TiltPositionWideAngle',
    0x3809: 'PrivacyMask1Data',
    0x380A: 'PrivacyMask1Style',
    0x380B: 'PrivacyMask1Corners',
    0x380C: 'PrivacyMask1ZoomThresholdMode',
    0x380D: 'PrivacyMask1ZoomThresholdValue',
    0x3810: 'PrivacyMask2',
    0x3FF0: 'PrivacyMask128',
    0x4000: 'PrivacyMaskEnable',
    0x4001: 'EnlargeEnable',
    0x4010: 'ModeOfOperation',
    0x4020: 'Compass',
    0x4021: 'Origin',
    0x4030: 'AzimuthElevation',
    0x4040: 'TurboMode',
    0x4050: 'PositionCorrection',
    0x4051: 'PanCorrectionMode',
    0x4052: 'MinPanCorrectionDrift',
    0x4053: 'TiltCorrectionMode',
    0x4054: 'MinTiltCorrectionDrift',
    0x4055: 'MaxDriftCorrection',
    0x4056: 'DriftCounters',
    0x4060: 'LatencyBufferSelection',
    0x4070: 'SingleClick',
    0x4071: 'XYCoordinates',
    0x4072: 'XCoordinate',
    0x4073: 'YCoordinate',
    0x4080: 'MaxRecordPlayBackMotorSpeed',
    0x4090: 'reserved',
    0x5000: 'PrePositionExtended1',
    0x5001: 'VisibleLightMode',
    0x5002: 'VisibleLightIntensity',
    0x5003: 'PresetIRMode',
    0x5004: 'PresetAuxMapping',
}

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