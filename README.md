# Pi-Shoot
Pi Shoot is a GUI camera application for Raspberry Pi with a remote SSH client.

# Install commands for Raspberry Pi.

`pip install customtkinter`

`pip install pyperclip`

`sudo apt install python3-pil.imagetk`

`sudo nano /etc/xdg/autostart/'Pi Shoot'.desktop`


### Add to file and save.
```
[Desktop Entry]
Name='Pi Shoot'
Exec=/usr/bin/python3 /home/pi/'Pi Shoot.py'
```


Add hdr.json file.


### Hardware
* GPIO 12 - Flash
* GPIO 26 - Shutter Button
* Screen Resolution 800x480
* Camera Resolution 9152x6944


# Install commands for SSH client.

Install pillow, customtkinter, pyperclip, and paramiko.
