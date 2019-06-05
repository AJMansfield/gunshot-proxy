import logging

from typing import List
from utils import DotDict

# Settings = the _description_ of the configuration
# Config = the actual configuration itself
# A Config is to Object like a Settings is to a Class

def load(*names:List[str], log:logging.Logger=logging.getLogger('config')) -> DotDict :
	import yaml
	import sys
	import collections
	try:
		with open('config.yaml', 'r') as f: # load config from file
			full_config = yaml.safe_load(f)

		config = {k:v for k,v in full_config.items() if k in names} # filter to just the requested configs
		
		for name in names:
			assert name in config # ensure all required configs are present
			if isinstance(config[name], collections.Mapping):
				assert config[name].get('enable', True) # and that the enable-able ones are all enabled
		
		config = DotDict(config) # allow dotted access
		return config
	except:
		sys.exit(6)

