import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')

import settings
config = settings.load('network', log=log.getChild('config'))

import socket
import sys
import os
import re

with open('/boot/cmdline.txt', 'r') as f:
    cmdline = f.read()
params = cmdline.split(' ')

oldparam = ""
for i in range(len(params)):
    if params[i].startswith("ip="):
        oldparam = params[i]
        break

# validate that all the IP addresses are valid or empty:
valid = True

# check that all IP addresses are valid
ip_fields=['client_ip','gw_ip','dns0_ip','dns1_ip','ntp0_ip']
for ip_field in ip_fields:
    if str(config.network.get(ip_field)) != "":
        try:
            socket.inet_aton(config.network.get(ip_field))
        except socket.error:
            log.error("Invalid {} value {}!".format(ip_field, config.network.get(ip_field)))
            valid = False

# check that netmask is valid
if str(config.network.get('netmask')) != "":
    try:
        netmask_bytes = socket.inet_aton(config.network.get('netmask'))
        netmask_bits = '{0:032b}'.format(sum(a*256**b for a,b in zip(netmask_bytes, range(3,-1,-1))))

        assert len(netmask_bits.split('10')) in {1,2}
        assert len(netmask_bits.split('01')) == 1
    except (socket.error, AssertionError):
        log.error("Invalid {} value {}!".format(ip_field, config.network.get(ip_field)))
        valid = False

# check that hostname is valid
if str(config.network.get('hostname')) != "":
    try:
        assert re.match(r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$', config.network.get('hostname'))
    except AssertionError:
        log.error("Invalid hostname value {}!".format(config.network.get('hostname')))
        valid = False


# check that autoconf is valid
if str(config.network.get('autoconf')) != "":
    try:
        assert config.network.get('autoconf') in {'none','any','dhcp','bootp','rarp','both'}
    except AssertionError:
        log.error("Invalid autoconf value {}!".format(config.network.get('autoconf')))
        valid = False


if not valid:
    log.error("Invalid configuration detected, exiting!")
    sys.exit(6)

template="ip={client_ip}::{gw_ip}:{netmask}:{hostname}::{autoconf}:{dns0_ip}:{dns1_ip}:{ntp0_ip}"

newparam = template.format(**config.network)

if oldparam != newparam:
    log.warning("Network settings changed, rebooting to apply the changes!")
    params[i] = newparam
    cmdline = ' '.join(params)
    with open('/tmp/cmdline.txt', 'w') as f:
        f.write(cmdline)
    os.system('sudo cp /tmp/cmdline.txt /boot/cmdline.txt')
    os.system('sudo systemctl reboot')