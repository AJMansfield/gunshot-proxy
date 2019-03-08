import datetime

settings = {
	'mqtt': {
		'host': '10.0.2.4',
	},
	'senseit_server': {
		'bind': ('10.0.2.4', 10001),
		'connect': ('10.0.0.100', 10002),
	},
	'senseit_client': {
		'listen': ('10.0.2.4', 10004),
	},
	'detector': {
		'listen': ('10.0.2.4', 10002),
	},
	
	'onvif_ptz': {
		'onvif': {
			'host': '10.0.2.3',
			'port': 80,
			'user': 'operator',
			'passwd': 'password',
		},
		'limits': {
			'az_min': -180,
			'az_max': 180,
			'az_off': 180,
			'el_min': 90,
			'el_max': 0,
			'el_off': 15,
			'z_min': 0,
			'z_max': 1,
			'z_off': 0,
		},
	},
	
	'onvif_relay': {
		'onvif': {
			'host': '10.0.2.3',
			'port': 80,
			'user': 'operator',
			'passwd': 'password',
		},
		'setup': [
			('SetRelayOutputSettings', {'RelayOutputToken':4, 'Properties': {'Mode': 'Monostable', 'DelayTime': datetime.timedelta(seconds=1), 'IdleState': 'open'}}),
		],
		'alarm': [
			('SetRelayOutputState', {'RelayOutputToken':4, 'LogicalState':'active'}),
		]
	},

	'osrd_ptz': {
		'addr': 0,
		'limits': {
			'az_min': 0,
			'az_max': 127999,
			'az_off': 0,
			'el_min': 0,
			'el_max': 31999,
			'el_off': 0,
		},
	},
}
