version = "v1.1 Jun/12/2023"


# Import modules
from PIL import Image, ImageTk
from time import strftime
from time import sleep
import RPi.GPIO as GPIO
import customtkinter
import pyperclip
import threading
import tkinter
import os


# Set theme
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")
customtkinter.set_widget_scaling(0.8)
customtkinter.set_window_scaling(1)


# Setup window
app = customtkinter.CTk()
app.minsize(800, 480)
app.maxsize(1920, 1080)
app.geometry("800, 480")
app.title("Pi Shoot                 " + version)


# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# Default Values
ssh = False
stop_checking_for_photo = False
focus_menu_not_fixed = True
last_mode = "Photo"
shutter_button_active = False


# Default Image
try:
    image = customtkinter.CTkImage(Image.open("/home/pi/Start Photo.png"), size=(500,375))
    image_label = customtkinter.CTkLabel(master=app, text="", image=image)
    image_label.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)
except:
    image_label = customtkinter.CTkLabel(master=app, text="")
    image_label.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)


def shutdown():
    os.system('sudo shutdown now')


def take_photo():
    global shutter_button_active

    choice = resolution_menu.get_option()

    if choice == "64MP":
        resolution = "--width 9152 --height 6944"
        maxsize_option = 1
    elif choice == "16MP":
        resolution = "--width 4624 --height 3472"
        maxsize_option = 1
    elif choice == "5MP":
        resolution = "--width 2592 --height 1944"
        maxsize_option = 1
    elif choice == "4MP":
        resolution = "--width 2312 --height 1736"
        maxsize_option = 1
    elif choice == "8K":
        resolution = "--width 7680 --height 4320"
        maxsize_option = 2
    elif choice == "4K":
        resolution = "--width 3840 --height 2160"
        maxsize_option = 2
    elif choice == "1080P":
        resolution = "--width 1920 --height 1080"
        maxsize_option = 2
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    choice = quality_menu.get_option()

    if choice == "100%":
        quality = "--quality 100"
    elif choice == "75%":
        quality = "--quality 75"
    elif choice == "50%":
        quality = "--quality 50"
    elif choice == "25%":
        quality = "--quality 25"
    
    choice = image_format_menu.get_option()

    if choice == "JPG":
        image_format = ".jpg"
    elif choice == "PNG":
        image_format = ".png"
    elif choice == "RAW 10":
        image_format = ".raw10"
    
    choice = timer_menu.get_option()

    if choice == "0s":
        timer = ""
    elif choice == "3s":
        timer = "--timeout 3000"
    elif choice == "5s":
        timer = "--timeout 5000"
    elif choice == "10s":
        timer = "--timeout 10000"
    elif choice == "30s":
        timer = "--timeout 30000"
    
    choice = focus_menu.get_option()
    
    if choice == "Autofocus":
        focus = "--autofocus-mode auto"
    elif choice == "Autofocus on Capture":
        focus = "--autofocus-on-capture"
    elif choice == "Continuous Autofocus":
        focus = "--autofocus-mode continuous"
    elif choice == "Manual":
        focus = lens_position.get_value()
    
    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()
    
    rotation = "--rotation " + rotation_menu.get_option()

    choice = hdr_menu.get_option()

    if choice == "Off":
        hdr = ""
    elif choice == "On":
        hdr = "--post-process-file hdr.json"
    
    if fullscreen_preview_checkbox.get() == 1:
        preview = "--fullscreen --preview"
    else:
        preview = "-p 112,224,400,300"
    
    if immediate_shutter_checkbox.get() == 1:
        immediate = "--immediate"
    else:
        immediate = ""

    date = strftime('%m-%d-%Y %H-%M-%S')
    photo_command = ("libcamera-still " + preview + " " + timer + " " + focus +  " " + rotation + " --viewfinder-width 2312 --viewfinder-height 1736 --denoise cdn_off " + quality + " " + resolution + " " + immediate + " " + shutter_speed + " " + gain.get_value() + " " + awbgains + " " + exposure_compensation.get_value() + " " + hdr + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " -o /home/pi/photos/'" + date + "'" + image_format + " &")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", photo_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)
    
    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)
    shutter_button_active = True
    os.system(photo_command)
    take_photo_button.configure(state="disabled")
    mode_menu.disable()

    def check_for_photo():
        global shutter_button_active
        date_c = date
        image_format_c = image_format

        if maxsize_option == 1:
            maxsize = (500, 375)
        elif maxsize_option == 2:
            maxsize = (500, 281)

        while True:
            if stop_checking_for_photo:
                if flash_on_capture:
                    GPIO.output(12, GPIO.LOW)
                break
            else:
                try:
                    image = customtkinter.CTkImage(Image.open("/home/pi/photos/" + date_c + image_format_c), size=(maxsize))
                    if flash_on_capture:
                        GPIO.output(12, GPIO.LOW)
                    image_label.configure(image=image)
                    take_photo_button.configure(state="normal")
                    shutter_button_active = False
                    mode_menu.enable()
                    break
                except:
                    sleep(1)

    threading.Thread(target=check_for_photo).start()


def take_video():
    global shutter_button_active

    choice = resolution_menu.get_option()

    if choice == "1080P 30FPS":
        resolution = "--width 1920 --height 1080 --framerate 30"
    elif choice == "720P 60FPS":
        resolution = "--width 1280 --height 720 --framerate 60"
    elif choice == "480P 90FPS":
        resolution = "--width 640 --height 480 --framerate 90"

    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()

    choice = focus_menu.get_option()
    
    if choice == "Autofocus":
        focus = "--autofocus-mode auto"
    elif choice == "Continuous Autofocus":
        focus = "--autofocus-mode continuous"
    elif choice == "Manual":
        focus = lens_position.get_value()

    rotation = "--rotation " + rotation_menu.get_option()

    date = strftime('%m-%d-%Y %H-%M-%S')
    video_command = ("libcamera-vid -p 112,224,400,300 -t 0 " + rotation + " " + focus + " " + resolution + " " + shutter_speed + " " + awbgains + " " + gain.get_value() + " " + exposure_compensation.get_value() + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " -o /home/pi/photos/""'" + date + "'.h264 &")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", video_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

    def stop_video():
        global shutter_button_active
        os.system('pkill libcamera-vid')
        shutter_button_active = False
        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)
        mode_menu.enable()
        os.system("ffmpeg -i /home/pi/photos/""'" + date + "'"".h264 -vcodec copy /home/pi/photos/""'" + date + "'.mp4")
        os.system("sudo rm /home/pi/photos/'" + date + ".h264'")
        take_photo_button.configure(text="Take Video", command=take_video)

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)
    os.system(video_command)
    take_photo_button.configure(text="Stop Video", command=stop_video)
    mode_menu.disable()
    shutter_button_active = True

    while True:
        if GPIO.input(26) == False:
            stop_video()
            break
        else:
            sleep(0.05)


def stream():
    global stream_link_button, shutter_button_active

    choice = resolution_menu.get_option()

    if choice == "1080P 30FPS":
        resolution = "--width 1920 --height 1080 --framerate 30"
    elif choice == "720P 60FPS":
        resolution = "--width 1280 --height 720 --framerate 60"
    elif choice == "480P 90FPS":
        resolution = "--width 640 --height 480 --framerate 90"
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()

    choice = focus_menu.get_option()
    
    if choice == "Autofocus":
        focus = "--autofocus-mode auto"
    elif choice == "Continuous Autofocus":
        focus = "--autofocus-mode continuous"
    elif choice == "Manual":
        focus = lens_position.get_value()
    
    choice = image_format_menu.get_option()

    if choice == "H.264":
        stream_format = ""
    elif choice == "MJPEG":
        choice = quality_menu.get_option()

        if choice == "100%":
            quality = "--quality 100"
        elif choice == "75%":
            quality = "--quality 75"
        elif choice == "50%":
            quality = "--quality 50"
        elif choice == "25%":
            quality = "--quality 25"
        stream_format = "--codec mjpeg " + quality

    choice = protocol_menu.get_option()

    protocol = ""
    protocol2 = ""

    if choice == "TCP":
        protocol = "--inline --listen -o tcp://0.0.0.0:8080"
    elif choice == "UDP":
        protocol = ""
    elif choice == "RSTP":
        protocol2 = "--inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8080/stream}' :demux=h264"

    rotation = "--rotation " + rotation_menu.get_option()

    #date = strftime('%m-%d-%Y %H-%M-%S')
    stream_command = ("libcamera-vid -p 112,224,400,300 -t 0 " + rotation + " " + stream_format + " " + protocol + " " + focus + " " + resolution + " " + shutter_speed + " " + awbgains + " " + gain.get_value() + " " + exposure_compensation.get_value() + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + protocol2 + " &")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", stream_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

    def copy_link_to_cb():

        if protocol_menu.get_option() == "TCP" and image_format_menu.get_option() == "H.264":
            pyperclip.copy("tcp/h264://<IP>:8080")
        elif protocol_menu.get_option() == "TCP" and image_format_menu.get_option() == "MJPEG":
            pyperclip.copy("tcp/mjpeg://<IP>:8080")
        elif protocol_menu.get_option() == "RSTP":
            pyperclip.copy("rtsp://<IP>:8080/stream")

    def end_stream():
        global shutter_button_active
        stream_link_button.delete()
        os.system('pkill libcamera-vid')
        shutter_button_active = False
        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)
        mode_menu.enable()

        take_photo_button.configure(text="Start Stream", command=stream)

    stream_link_button = Button("Copy Stream Link to Clipboard", copy_link_to_cb, 0.775, 0.55)
    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)
    os.system(stream_command)
    take_photo_button.configure(text="End Stream", command=end_stream)
    mode_menu.disable()
    shutter_button_active = True

    while True:
        if GPIO.input(26) == False:
            end_stream()
            break
        else:
            sleep(0.05)


def preview():
    global preview_active, shutter_button_active
    choice = resolution_menu.get_option()

    if choice == "4MP":
        resolution = "--viewfinder-width 2312 --viewfinder-height 1736"
    elif choice == "1080P":
        resolution = "--viewfinder-width 1920 --viewfinder-height 1080"
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    choice = quality_menu.get_option()

    if choice == "100%":
        quality = "--quality 100"
    elif choice == "75%":
        quality = "--quality 75"
    elif choice == "50%":
        quality = "--quality 50"
    elif choice == "25%":
        quality = "--quality 25"
    
    choice = timer_menu.get_option()

    if choice == "0s":
        timer = ""
    elif choice == "3s":
        timer = "-t 3000"
    elif choice == "5s":
        timer = "-t 5000"
    elif choice == "10s":
        timer = "-t 10000"
    elif choice == "30s":
        timer = "-t 30000"
    
    choice = focus_menu.get_option()
    
    if choice == "Autofocus":
        focus = "--autofocus-mode auto"
    elif choice == "Autofocus on Capture":
        focus = "--autofocus-on-capture"
    elif choice == "Continuous Autofocus":
        focus = "--autofocus-mode continuous"
    elif choice == "Manual":
        focus = lens_position.get_value()
    
    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()
    
    rotation = "--rotation " + rotation_menu.get_option()

    choice = hdr_menu.get_option()

    if choice == "Off":
        hdr = ""
    elif choice == "On":
        hdr = "--post-process-file hdr.json"

    preview_command = ("libcamera-still -p 112,224,400,300 -t 0 " + rotation + " " + timer + " " + focus + " --denoise cdn_off " + quality + " " + resolution + " " + shutter_speed + " " + gain.get_value() + " " + awbgains + " " + exposure_compensation.get_value() + " " + hdr + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " &")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", preview_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)
    
    def stop_preview():
        global preview_active, shutter_button_active
        os.system('pkill libcamera-still')
        shutter_button_active = False
        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)
        take_photo_button.configure(text="Start Preview", command=preview)
        preview_active = False
        mode_menu.enable()

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)
    os.system(preview_command)
    take_photo_button.configure(text="Stop Preview", command=stop_preview)
    preview_active = True
    mode_menu.disable()
    shutter_button_active = True

    while True:
        if GPIO.input(26) == False:
            stop_preview()
            break
        else:
            sleep(0.05)


def update(choice="", value=""):
    global focus_menu_not_fixed, last_mode
    
    if focus_menu.get_option() == "Manual" and focus_menu_not_fixed:
        lens_position.enable("Lens Position")
        focus_menu_not_fixed = False
    elif focus_menu.get_option() == "Manual":
        pass
    else:
        lens_position.disable("Lens Position Auto")
        focus_menu_not_fixed = True
    
    if awb_red_gain.get_value() == "":
        awb_blue_gain.enable("AWB Blue Gain Auto")
    if awb_blue_gain.get_value() == "":
        awb_red_gain.enable("AWB Red Gain Auto")
    
    if protocol_menu.get_option() == "RSTP":
        image_format_menu.disable("H.264")
    elif protocol_menu.get_option() == "TCP" or protocol_menu.get_option() == "UDP":
        image_format_menu.enable()
    
    if image_format_menu.get_option() == "MJPEG":
        quality_menu.enable()
    elif image_format_menu.get_option() == "H.264":
        quality_menu.disable("100%")
    
    if hdr_menu.get_option() == "On":
        resolution_menu.change_options(["16MP", "5MP", "4MP", "4K", "1080P"])
        if resolution_menu.get_option() == "64MP" or resolution_menu.get_option() == "8K":
            resolution_menu.set_option("16MP")
    elif hdr_menu.get_option() == "Off" and mode_menu.get_option() != "Preview":
        resolution_menu.change_options(["64MP", "16MP", "5MP", "4MP", "8K", "4K", "1080P"])

    if mode_menu.get_option() == "Photo" and last_mode != "Photo":
        take_photo_button.configure(text="Take Photo", command=take_photo)
        resolution_menu.redef("64MP", ["64MP", "16MP", "5MP", "4MP", "8K", "4K", "1080P"])
        shutter_speed_menu.redef("Auto", ["Auto", "420", "360", "300", "240", "180", "120", "60", "30", "15", "1", "1/15", "1/30", "1/60", "1/120", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000", "1/4000", "1/8000"], "Shutter Speed")
        shutter_speed_menu.enable()
        quality_menu.enable()
        image_format_menu.redef("JPG", ["JPG", "PNG", "RAW 10"])
        image_format_menu.enable()
        timer_menu.enable()
        focus_menu.redef("Autofocus on Capture", ["Autofocus", "Autofocus on Capture", "Manual", "Continuous Autofocus"])
        protocol_menu.disable("None")
        hdr_menu.enable("Off")
        fullscreen_preview_checkbox.configure(state="normal")
        immediate_shutter_checkbox.configure(state="normal")
        last_mode = "Photo"

    elif mode_menu.get_option() == "Video" and last_mode != "Video":
        take_photo_button.configure(text="Take Video", command=take_video)
        resolution_menu.redef("1080P 30FPS", ["1080P 30FPS", "720P 60FPS", "480P 90FPS"])
        shutter_speed_menu.redef("Auto", ["Auto", "1/30", "1/60", "1/90", "1/120"], "Shutter Speed")
        quality_menu.disable("100%")
        image_format_menu.disable("MP4")
        timer_menu.disable("0s")
        focus_menu.redef("Continuous Autofocus", ["Autofocus", "Manual", "Continuous Autofocus"])
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        fullscreen_preview_checkbox.configure(state="disabled")
        fullscreen_preview_checkbox.deselect()
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Video"
    
    elif mode_menu.get_option() == "Stream" and last_mode != "Stream":
        take_photo_button.configure(text="Start Stream", command=stream)
        resolution_menu.redef("1080P 30FPS", ["1080P 30FPS", "720P 60FPS", "480P 90FPS"])
        quality_menu.disable("100%")
        shutter_speed_menu.redef("Auto", ["Auto", "1/30", "1/60", "1/90", "1/120"], "Shutter Speed")
        image_format_menu.redef("H.264", ["H.264", "MJPEG"])
        image_format_menu.enable()
        timer_menu.disable("0s")
        focus_menu.redef("Continuous Autofocus", ["Autofocus", "Manual", "Continuous Autofocus"])
        protocol_menu.enable("TCP")
        hdr_menu.disable("Off")
        fullscreen_preview_checkbox.configure(state="disabled")
        fullscreen_preview_checkbox.deselect()
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Stream"
    
    elif mode_menu.get_option() == "Preview" and last_mode != "Preview":
        take_photo_button.configure(text="Start Preview", command=preview)
        resolution_menu.redef("4MP", ["4MP", "1080P"])
        shutter_speed_menu.redef("Auto", ["Auto", "420", "360", "300", "240", "180", "120", "60", "30", "15", "1", "1/15", "1/30", "1/60", "1/120", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000", "1/4000", "1/8000"], "Shutter Speed")
        shutter_speed_menu.enable()
        quality_menu.disable()
        image_format_menu.set_option("None")
        image_format_menu.disable()
        timer_menu.disable("0s")
        focus_menu.redef("Autofocus on Capture", ["Autofocus", "Autofocus on Capture", "Manual", "Continuous Autofocus"])
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        fullscreen_preview_checkbox.configure(state="disabled")
        fullscreen_preview_checkbox.deselect()
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Preview"
    
    if mode_menu.get_option() == "Preview" and preview_active:
        os.system('pkill libcamera-still')
        preview()


class DropDownMenu():

    def __init__(self, name, default_option, locationx, locationy, options):
        self.label = customtkinter.CTkLabel(master=app, text=name, justify=customtkinter.LEFT)
        self.label.place(relx=locationx, rely=(locationy - 0.05), anchor=tkinter.CENTER)
        self.optionmenu = customtkinter.CTkOptionMenu(app, values=options, command=update)
        self.optionmenu.set(default_option)
        self.optionmenu.place(relx=locationx, rely=locationy, anchor=tkinter.CENTER)
        self.name = name
        
    
    def disable(self, option=""):
        if option == "":
            option = self.optionmenu.get()
        self.optionmenu.configure(state="disabled")
        self.optionmenu.set(option)
    
    def enable(self, option=""):
        if option == "":
            option = self.optionmenu.get()
        self.optionmenu.configure(state="normal")
        self.optionmenu.set(option)
    
    def get_option(self):
        return self.optionmenu.get()

    def change_options(self, options):
        self.optionmenu.configure(values=options)
    
    def set_option(self, option):
        self.optionmenu.set(option)
    
    def change_label(self, label):
        self.label.configure(text=label)
    
    def redef(self, option, options, name=""):
        if name == "":
            name = self.name
        self.label.configure(text=name)
        self.optionmenu.set(option)
        self.optionmenu.configure(values=options)


class Slider:
    
    def __init__(self, name, command, range_from, range_to, locationx, locationy, round_place, auto=False):
        if auto:
            label = customtkinter.CTkLabel(master=app, text=(name + " Auto"), justify=customtkinter.LEFT)
        else:
            label = customtkinter.CTkLabel(master=app, text=(name + " "), justify=customtkinter.LEFT)
        label.place(relx=locationx, rely=(locationy - 0.05), anchor=tkinter.CENTER)
        slider = customtkinter.CTkSlider(app, from_=range_from, to=range_to, orientation="horizontal", command=self.__update)
        slider.place(relx=locationx, rely=locationy, anchor=tkinter.CENTER)
        self.label = label
        self.name = name
        self.round_place = round_place
        self.slider = slider
        self.command = command
        self.auto = auto
        self.range_from = range_from
    

    def __update(self, value):
        update()
        self.value = str(round(value, self.round_place))

        if self.auto and float(self.value) == self.range_from:
            self.label.configure(text = self.name + " Auto")
        else:
            self.label.configure(text = self.name + " " + self.value)
    
    def get_value(self):
        try:
            if self.auto and float(self.value) == self.range_from:
                return ""
            else:
                return self.command + " " + self.value
        except:
            return ""
    
    def enable(self, text=""):
        self.slider.configure(state="normal")

        if text == "":
            self.label.configure(text = self.name)
        else:
            self.label.configure(text = text)
    
    def disable(self, text=""):
        self.slider.configure(state="disabled")

        if text == "":
            self.label.configure(text = self.name)
        else:
            self.label.configure(text = text)


class Button:

    def __init__(self, text, command, locationx, locationy):
        self.button = customtkinter.CTkButton(master=app, text=text, command=command)
        self.button.place(relx=locationx, rely=locationy, anchor=tkinter.CENTER)
    
    def delete(self):
        self.button.destroy()


lens_position = Slider("Lens Position", "--lens-position", 0, 12, 0.1, 0.3, 1)
lens_position.disable("Lens Position Auto")

gain = Slider("Gain", "--gain", 0, 232, 0.3, 0.3, 0, auto=True)
awb_red_gain = Slider("AWB Red Gain", "", 0, 10, 0.5, 0.3, 1, auto=True)
awb_blue_gain = Slider("AWB Blue Gain", "", 0, 10, 0.7, 0.3, 1, auto=True)
exposure_compensation = Slider("Exposure Compensation", "--ev", -25, 25, 0.9, 0.3, 0)
brightness = Slider("Brightness", "--brightness", -1, 1, 0.7, 0.4, 2)
contrast = Slider("Contrast", "--contrast", 0, 2, 0.9, 0.4, 2)
saturation = Slider("Saturation", "--saturation", 0, 2, 0.7, 0.5, 2)
sharpness = Slider("Sharpness", "--sharpness", 0, 2, 0.9, 0.5, 2)
digital_zoom = Slider("Digital Zoom", "", 0, 10, 0.9, 0.2, 1)

mode_menu = DropDownMenu("Mode", "Photo", 0.1, 0.1, ["Photo", "Video", "Stream", "Preview"])
resolution_menu = DropDownMenu("Resolution", "64MP", 0.25, 0.1, ["64MP", "16MP", "5MP", "4MP", "8K", "4K", "1080P"])
shutter_speed_menu = DropDownMenu("Shutter Speed", "Auto", 0.4, 0.1, ["Auto", "420", "360", "300", "240", "180", "120", "60", "30", "15", "1", "1/15", "1/30", "1/60", "1/120", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000", "1/4000", "1/8000"])
quality_menu = DropDownMenu("Quality", "100%", 0.55, 0.1, ["100%", "75%", "50%", "25%"])
image_format_menu = DropDownMenu("Format", "JPG", 0.7, 0.1, ["JPG", "PNG", "RAW 10"])
timer_menu = DropDownMenu("Timer", "0s", 0.85, 0.1, ["0s", "3s", "5s", "10s", "30s"])
focus_menu = DropDownMenu("Focus", "Autofocus on Capture", 0.1, 0.2, ["Autofocus", "Autofocus on Capture", "Manual", "Continuous Autofocus"])
flash_menu = DropDownMenu("Flash", "Off", 0.25, 0.2, ["On Capture", "On", "Off"])
protocol_menu = DropDownMenu("Protocol", "None", 0.4, 0.2, ["TCP", "UDP", "RSTP"])
protocol_menu.disable()
rotation_menu = DropDownMenu("Rotation", "180", 0.55, 0.2, ["0", "180"])
hdr_menu = DropDownMenu("HDR", "Off", 0.7, 0.2, ["Off", "On"])

shutdown_button = customtkinter.CTkButton(master=app, text="Shutdown", command=shutdown)
shutdown_button.place(relx=0.7, rely=0.8, anchor=tkinter.CENTER)
take_photo_button = customtkinter.CTkButton(master=app, text="Take Photo", command=take_photo)
take_photo_button.place(relx=0.85, rely=0.575, anchor=tkinter.CENTER)

fullscreen_preview_checkbox = customtkinter.CTkCheckBox(master=app, text="Fullscreen Preview")
fullscreen_preview_checkbox.place(relx=0.85, rely=0.875, anchor=tkinter.CENTER)
immediate_shutter_checkbox = customtkinter.CTkCheckBox(master=app, text="IS")
immediate_shutter_checkbox.place(relx=0.99, rely=0.1, anchor=tkinter.CENTER)

command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
command_textbox.insert("0.0", "")
command_textbox.configure(state="disabled")
command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

def check_flash_and_shutter_button():
    global flash_on_capture
    while True:
        if flash_menu.get_option() == "On":
            GPIO.output(12, GPIO.HIGH)
            flash_on_capture = False
            last_flash_mode = "On"
        elif flash_menu.get_option() == "On Capture" and last_flash_mode != "On Capture":
            GPIO.output(12, GPIO.LOW)
            flash_on_capture = True
            last_flash_mode = "On Capture"
        elif flash_menu.get_option() == "Off":
            GPIO.output(12, GPIO.LOW)
            flash_on_capture = False
            last_flash_mode = "Off"
        
        if GPIO.input(26) == False and shutter_button_active == False:
            if mode_menu.get_option() == "Photo":
                take_photo()
            elif mode_menu.get_option() == "Video":
                take_video()
            elif mode_menu.get_option() == "Stream":
                stream()
            elif mode_menu.get_option() == "Preview":
                preview()

        sleep(0.075)

threading.Thread(target=check_flash_and_shutter_button).start()


app.mainloop()
