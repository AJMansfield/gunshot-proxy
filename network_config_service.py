import logging
logging.basicConfig(level=logging.INFO)

log = logging.getLogger('')

import settings
config = settings.load('network', log=log.getChild('config'))

import os

template="ip={client_ip}::{gw_ip}:{netmask}:{hostname}::{autoconf}:{dns0_ip}:{dns1_ip}:{ntp0_ip}"

with open('cmdline.txt', 'r') as f:
    cmdline = f.read()
params = cmdline.split(' ')

oldparam = ""
for i in range(len(params)):
    if params[i].startswith("ip="):
        oldparam = params[i]
        break

newparam = template.format(**config.network)

if oldparam != newparam:
    log.warning("Network settings changed, rebooting to apply the changes!")
    params[i] = newparam
    cmdline = ' '.join(params)
    with open('/tmp/cmdline.txt', 'w') as f:
        f.write(cmdline)
    os.system('sudo cp /tmp/cmdline.txt /boot/cmdline.txt')
    os.system('sudo systemctl reboot')