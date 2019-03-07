Proxy software for running on a local Raspberry Pi inside each gunshot detector.

Proxies GSD traffic from the gunshot detector to the Sentri Server,
  parsing each packet and issuing the correct ONVIF PTZ commands locally
  rather than depending on the Sentri Server to command the camera.

### Installation

```sh
sudo apt install python3 python3-pip python3-lxml python3-scapy mosquitto
pip3 install -r requirements.txt
cp wsdl/ /home/pi/.local/lib/python3.5/site-packages/
sudo cp *.service /etc/systemd/system/
sudo cp gunshot.target /etc/systend/system/
sudo systemctl daemon-reload
sudo systemctl enable gunshot.target
sudo systemctl reboot
```

### Architecture

A bunch of separate microservices that all connect to a single MQTT service.

Topics:
- `sentri/detector/event/raw`
  Subscribe to this one to recieve everything the GSD emits.
- `sentri/detector/command/raw`
  Publish here to submit commands to the GSD.