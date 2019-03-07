
settings = {
	#'server': 'sentri://10.0.0.200:10002', # *THIS* device, the one running the proxy
	#'conn': 'tunnel://10.0.0.100:10002', # The Sentri Server
	'gunshot': {
		'local': {
			'host': '10.0.0.200',
			'port': 10002,
		},
		'remote': {
			'host': '10.0.2.2',
			'port': 10001,
		},
	},
	'sentri': {
		'local': {
			'host': '10.0.0.200',
			'port': 10001,
		},
		'remote': {
			'host': '10.0.0.100',
			'port': 10002,
		},
	},
	'cal': {
		'local': {
			'host': '10.0.0.200',
			'port': 10004,
		},
	},
	
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
