from setuptools import setup

setup(
	name='gsd-proxy',
	version='0.1',
	description='Tool for proxying gunshot detector alarms and issuing local camera commands.',
	author='Anson Mansfield',
	author_email='amansfield@mantaro.com',
	packages=['gsd_proxy'],
	install_requires=[
		'angles',
		'onvif-zeep',
        'pproxy',
        'scapy',
	],
	zip_safe=False,
	test_suite='nose.collector',
	tests_require=['nose', 'mock', 'coverage'],
)	