Proxy software for running on a local Raspberry Pi inside each gunshot detector.

Proxies GSD traffic from the gunshot detector to the Sentri Server,
  parsing each packet and issuing the correct ONVIF PTZ commands locally
  rather than depending on the Sentri Server to command the camera.

To install (WIP):

- install the python package: `pip install -e ./gsdproxy`
- install the wsdl files
- configure the settings file: `nano settings.py`
- copy or link the .service file
  - link: `ln -s gsdproxy.service -t /etc/systemd/system/`
  - copy: `cp gsdproxy.service /etc/systemd/system/`
- reload systemd services: `systemctl daemon-reload`
- enable the service: `systemctl enable gsdproxy`
- reboot: `systemctl reboot`


### Architecture

A bunch of separate microservices that all connect to a single MQTT service.

Topics:
- `sentri/detector/event/raw`
  Subscribe to this one to recieve everything the GSD emits.
- `sentri/detector/command/raw`
  Publish here to submit commands to the GSD.