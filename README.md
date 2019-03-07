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

A bunch of separate microservices that all connect to a single MQTT broker to pass messages.

Topics:
- `sentri/detector/event/raw`
  Subscribe to this one to recieve everything the GSD emits.
- `sentri/detector/command/raw`
  Publish here to submit commands to the GSD.

This decouples the different aspects of the functionality from each other, so a single failed microservice does not inhibit any other functionality.
Services are free to (and in fact are expected to) crash if and when they encounter a failure condition, such as inability to connect to a required network port;
  fault tolerance is achieved by automatically restarting failed units at the service layer.

This also makes the design modular; for instance in an environment without a central server the `sentri_server` service can simply be omitted.
Additional custom modules can be added by subscribing and publishing to these channels.
