Proxy software for running on a local Raspberry Pi inside each gunshot detector.

Proxies GSD traffic from the gunshot detector to the Sentri Server,
  parsing each packet and issuing the correct ONVIF PTZ commands locally
  rather than depending on the Sentri Server to command the camera.

### Installation

```sh
# Install packages
sudo apt install python3 python3-pip python3-lxml python3-scapy python3-yaml mosquitto apache2 php php-yaml
pip3 install -r requirements.txt

# Install WDSL files
cp -r wsdl/ /home/pi/.local/lib/python3.5/site-packages/

# Create admin user for managing the script
sudo useradd admin
# Set up the required groups and sudoers permissions
sudo usermod -aG pi admin
sudo cp gunshot_sudoers /etc/sudoers.d/

# Install settings page
sudo cp -r settings-site/* /var/www/html/

# Install and enable systemd services
sudo cp *.service /etc/systemd/system/
sudo cp gunshot.target /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable gunshot.target
sudo systemctl enable gunshot@senseit_server.service
sudo systemctl enable gunshot@senseit_client.service
sudo systemctl enable gunshot@detector.service
sudo systemctl enable gunshot@onvif_ptz.service
sudo systemctl enable gunshot@onvif_relay.service
sudo systemctl enable gunshot@rcp_ptz.service
sudo systemctl enable gunshot_network_config.service

# Reboot the system
sudo systemctl reboot
```

You can now navigate to the Pi's IP address in your browser and configure the scripts there.

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
