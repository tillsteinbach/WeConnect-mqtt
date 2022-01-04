# Install WeConnect-MQTT as a service on on operating systems providing systemd

## How to install
Open file weconnect-mqtt.service and change the username and commandline parameters according to your needs

Copy the unit file to /etc/systemd/system and give it permissions:
```bash
sudo cp weconnect-mqtt.service /etc/systemd/system/weconnect-mqtt.service
sudo chmod 644 /etc/systemd/system/weconnect-mqtt.service
```

## How to start
Once you have installed the file, you are ready to test the service:
```bash
sudo systemctl start weconnect-mqtt
sudo systemctl status weconnect-mqtt
```

The service can be stopped or restarted using standard systemd commands:
```bash
sudo systemctl stop weconnect-mqtt
sudo systemctl restart weconnect-mqtt
```

## How to enable autostart after boot
Finally, use the enable command to ensure that the service starts whenever the system boots:
```bash
sudo systemctl enable weconnect-mqtt
```
