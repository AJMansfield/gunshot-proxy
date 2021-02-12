import logging

from typing import List
from utils import DotDict
import collections

# Settings = the _description_ of the configuration
# Config = the actual configuration itself
# A Config is to Object like a Settings is to a Class

def verify_entry(name, config):
	if '.' in name:
		name, rest = name.split('.', 1)
		assert name in config
		if isinstance(config[name], collections.Mapping):
			assert config[name].get('enable', True)
		verify_entry(rest, config[name])
	else:
		assert name in config
		if isinstance(config[name], collections.Mapping):
			assert config[name].get('enable', True)

def load(*names:List[str], log:logging.Logger=logging.getLogger('config')) -> DotDict :
	import yaml
	import sys
	import collections
	try:
		with open('config.yaml', 'r') as f: # load config from file
			full_config = yaml.safe_load(f)

		config = {k:v for k,v in full_config.items() if k in names} # filter to just the requested configs
		
		for name in names:
			verify_entry(name, config)
		
		config = DotDict(config) # allow dotted access
		return config
	except:
		sys.exit(6) # exit status 6/NOTCONFIGURED

