# Pi Shoot
Pi Shoot is a Python GUI camera application for Raspberry Pi, with a SSH client for accessing the camera remotely.
<br>
<br>

# Pi Shoot Install Commands
Note: `/home/pi` will need to be replaced if you installed in a different directory, or use a different user than `pi`. Additional it will need to be replaced in the `Pi Shoot.desktop` file.
```
sudo apt install python3 python3-dev python3-venv python3-pip python3-pil.imagetk git
git clone https://github.com/JM400/Pi-Shoot.git --branch development
cd Pi-Shoot/
python3 -m venv venv/
venv/bin/python3 -m pip install -r requirements.txt
cp 'Pi Shoot.desktop' /home/pi/Desktop/
```
<br>

You can now run Pi Shoot by clicking the icon on the desktop or with:
```
/home/pi/Pi-Shoot/venv/bin/python3 /home/pi/Pi-Shoot/'Pi Shoot.py'
```
<br>

You can have Pi Shoot start on boot by running:
```
sudo cp 'Pi Shoot.desktop' /etc/xdg/autostart/'Pi Shoot.desktop'
```

## Hardware
### Shutter Button 
Connect a button to GND and GPIO pin 26, no pull up resistor is needed an internal one is already used.
### Flash
Pi Shoot sends a high signal on GPIO pin 12 if flash is selected. A high power LED should not be connected directly to a GPIO pin. Instead a LED module that uses a switch should be used, or a circuit can be built with a transistor to control the LED.
<br>
<br>

# Pi Shoot SSH Client Install Commands
