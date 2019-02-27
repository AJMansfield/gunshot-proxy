
settings = {
	'server': 'sentri://10.0.0.200:10002', # *THIS* device, the one running the proxy
	'conn': 'tunnel://10.0.0.100:10002', # The Sentri Server
	
	'camera': {
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
	
}
