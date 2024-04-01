version = "v1.1.0 Apr/1/2024" # v1.0.0 Jun/12/2023


# Import modules
from PIL import Image, ImageTk
from time import strftime
from time import sleep
import RPi.GPIO as GPIO
import customtkinter
import pyperclip
import threading
import tkinter
import sys
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
closing = False
ssh = False
stop_checking_for_photo = False
last_mode = "Photo"
shutter_button_active = False
shutter_read_delay = 0.5
preview_active = False
resolution_list = ["64MP", "48MP", "16MP Arducam", "16MP Binned", "12.3MP HQ", "11.9MP V3", "8MP V2", "5MP V1", "1.58MP GS", "8K", "4K", "1440P", "1080P", "720P"]
low_resolution_list = ["16MP Arducam", "16MP Binned", "12.3MP HQ", "11.9MP V3", "8MP V2", "5MP V1", "1.58MP GS", "4K", "1440P", "1080P", "720P"]
resolution_default = "64MP"
low_resolution_default = "16MP Binned"
photo_focus_list = ["Auto", "Autofocus on Capture", "Manual", "Continuous", "Fixed", "Default"]
video_focus_list = ["Auto", "Manual", "Continuous", "Fixed", "Default"]
default_photo_focus = "Autofocus on Capture"
default_video_focus = "Continuous"
video_resolution_list = ["1080P 30FPS", "720P 60FPS", "1024 x 768 30FPS", "480P 90FPS"]
default_video_resolution = "1080P 30FPS"
photo_shutter_speeds = ["Auto", "420", "360", "300", "240", "180", "120", "60", "30", "15", "1", "1/15", "1/30", "1/60", "1/120", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000", "1/4000"]
default_photo_shutter_speed = "Auto"
video_shutter_speeds = ["Auto", "1/30", "1/60", "1/90", "1/120", "1/150", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000", "1/4000"]
default_video_shutter_speed = "Auto"


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


def on_closing():
    global closing
    closing = True
    sleep(2)
    app.destroy()
    os.system("pkill -f 'Pi Shoot.py'")


def camera_reset():
    global shutter_button_active
    
    os.system("pkill -f 'libcamera'")
    shutter_button_active = False
    take_photo_button.configure(state="normal")
    mode_menu.enable()


def calculate_digital_zoom():
    try:
        zoom = float(digital_zoom.get_value().strip())
    
    except:
        return ""
    
    if zoom == "":
        return ""
    elif zoom == 1:
        return "--roi 0.00,0.00,1.00,1.00"
    elif zoom == 2:
        return "--roi 0.25,0.25,0.50,0.50"
    elif zoom == 3:
        return "--roi 0.375,0.375,0.25,0.25"
    elif zoom == 4:
        return "--roi 0.4375,0.4375,0.125,0.125"
    elif zoom == 5:
        return "--roi 0.46875,0.46875,0.0625,0.0625"
    else:
        return ""


def get_resolution():
    global maxsize_option

    resolution = resolution_menu.get_option()

    if resolution == "64MP":
        maxsize_option = 1
        return "--width 9152 --height 6944"
    
    elif resolution == "48MP":
        maxsize_option = 1
        return "--width 8000 --height 6000"
    
    elif resolution == "16MP Arducam":
        maxsize_option = 1
        return "--width 4656 --height 3496"
    
    elif resolution == "16MP Binned":
        maxsize_option = 1
        return "--width 4624 --height 3472"
    
    elif resolution == "12.3MP HQ":
        maxsize_option = 1
        return "--width 4056 --height 3040"
    
    elif resolution == "11.9MP V3":
        maxsize_option = 1
        return "--width 4608 --height 2592"
    
    elif resolution == "8MP V2":
        maxsize_option = 1
        return "--width 3280 --height 2464"
    
    elif resolution == "5MP V1":
        maxsize_option = 1
        return "--width 2592 --height 1944"
    
    elif resolution == "1.58MP GS":
        maxsize_option = 1
        return "--width 1456 --height 1088"
    
    elif resolution == "8K":
        maxsize_option = 2
        return "--width 7680 --height 4320"

    elif resolution == "4K":
        maxsize_option = 2
        return "--width 3840 --height 2160"
    
    elif resolution == "1440P":
        maxsize_option = 2
        return "--width 2560 --height 1440"
    
    elif resolution == "1080P":
        maxsize_option = 2
        return "--width 1920 --height 1080 --mode 1920:1080"
    
    elif resolution == "720P":
        maxsize_option = 2
        return "--width 1280 --height 720"

    elif resolution == "1080P 30FPS":
        maxsize_option = 0
        return "--width 1920 --height 1080 --framerate 30"

    elif resolution == "720P 60FPS":
        maxsize_option = 0
        return "--width 1280 --height 720 --framerate 60"
    
    elif resolution == "1024 x 768 30FPS":
        maxsize_option = 0
        return "--width 1024 --height 768 --framerate 30"

    elif resolution == "480P 90FPS":
        maxsize_option = 0
        return "--width 640 --height 480 --framerate 90"
    
    else:
        maxsize_option = -1
        return ""


def get_focus():
    focus = focus_menu.get_option()
    
    if focus == "Auto":
        return "--autofocus-mode auto"

    elif focus == "Autofocus on Capture":
        return "--autofocus-mode auto --autofocus-on-capture"

    elif focus == "Continuous":
        return "--autofocus-mode continuous"

    elif focus == "Manual":
        return "--autofocus-mode manual " + lens_position.get_value()

    elif focus == "Fixed":
        return "--autofocus-mode manual --lens-position 6.1"
    
    elif focus == "Default":
        return "--autofocus-mode default"

    else:
        return ""


def get_image_format():
    choice = image_format_menu.get_option()

    if choice == "JPG":
        return ".jpg -e jpg"
    elif choice == "PNG":
        return ".png -e png"
    elif choice == "RAW + JPG":
        return ".jpg -r"


def take_photo():
    global shutter_button_active
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    choice = quality_menu.get_option()
    quality = "--quality " + choice.strip("%")
    choice = timer_menu.get_option()

    if choice == "0s":
        timer = ""
    else:
        timer = "--timeout " + str(int(choice.strip("s")) * 1000)
    
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
        preview = "-p 35,192,400,250"
    
    if immediate_shutter_checkbox.get() == 1:
        immediate = "--immediate"
    else:
        immediate = ""

    date = strftime('%m-%d-%Y %H-%M-%S')
    photo_command = ("libcamera-still " + preview + " " + timer + " " + get_focus() +  " " + rotation + " --viewfinder-width 2312 --viewfinder-height 1736 --denoise cdn_off " + quality + " " + get_resolution() + " " + immediate + " " + shutter_speed + " " + gain.get_value() + " " + awbgains + " " + exposure_compensation.get_value() + " " + hdr + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + " -o /home/pi/photos/'" + date + "'" + get_image_format() + " &")
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
        image_format_c, encode = get_image_format().split(" -")

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

    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()

    rotation = "--rotation " + rotation_menu.get_option()

    if fullscreen_preview_checkbox.get() == 1:
        preview = "-p 0,0,480,800"
    else:
        preview = "-p 35,192,400,250"

    date = strftime('%m-%d-%Y %H-%M-%S')
    video_command = ("libcamera-vid -t 0 " + preview + " " + rotation + " " + get_focus() + " " + get_resolution() + " " + shutter_speed + " " + awbgains + " " + gain.get_value() + " " + exposure_compensation.get_value() + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + " -o /home/pi/photos/""'" + date + "'.h264 &")
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
        os.system("ffmpeg -i /home/pi/photos/""'" + date + "'"".h264 -vcodec copy /home/pi/photos/""'" + date + "'.mp4")
        os.system("sudo rm /home/pi/photos/'" + date + ".h264'")
        sleep(1)
        mode_menu.enable()
        take_photo_button.configure(text="Take Video", command=take_video)

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)

    os.system(video_command)
    sleep(1)
    take_photo_button.configure(text="Stop Video", command=stop_video)
    mode_menu.disable()
    shutter_button_active = True

    def video_loop():
        while True:
            if GPIO.input(26) == False:
                stop_video()
                sleep(1)
                break
            else:
                sleep(shutter_read_delay)
    
    threading.Thread(target=video_loop).start()


def stream():
    global stream_link_button, shutter_button_active
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()
    
    choice = image_format_menu.get_option()

    if choice == "H.264":
        stream_format = ""
    elif choice == "MJPEG":
        choice = quality_menu.get_option()
        quality = "--quality " + choice.strip("%")
        stream_format = "--codec mjpeg " + quality

    choice = protocol_menu.get_option()

    protocol = ""
    protocol2 = ""

    if choice == "TCP":
        protocol = "--inline --listen -o tcp://0.0.0.0:8080"
    elif choice == "UDP":
        protocol = ""
    elif choice == "RTSP":
        protocol2 = "--inline -o - | cvlc stream:///dev/stdin --sout '#rtp{sdp=rtsp://:8080/stream}' :demux=h264"

    rotation = "--rotation " + rotation_menu.get_option()

    if fullscreen_preview_checkbox.get() == 1:
        preview = "-p 0,0,480,800"
    else:
        preview = "-p 35,192,400,250"

    #date = strftime('%m-%d-%Y %H-%M-%S')
    stream_command = ("libcamera-vid -t 0 " + preview + " " + rotation + " " + stream_format + " " + protocol + " " + get_focus() + " " + get_resolution() + " " + shutter_speed + " " + awbgains + " " + gain.get_value() + " " + exposure_compensation.get_value() + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + " " + protocol2 + " &")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", stream_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

    def copy_link_to_cb():

        if protocol_menu.get_option() == "TCP" and image_format_menu.get_option() == "H.264":
            pyperclip.copy("tcp/h264://<IP>:8080")
        elif protocol_menu.get_option() == "TCP" and image_format_menu.get_option() == "MJPEG":
            pyperclip.copy("tcp/mjpeg://<IP>:8080")
        elif protocol_menu.get_option() == "RTSP":
            pyperclip.copy("rtsp://<IP>:8080/stream")

    def end_stream():
        global shutter_button_active
        stream_link_button.delete()
        os.system('pkill libcamera-vid')
        shutter_button_active = False

        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)

        sleep(1)
        mode_menu.enable()
        take_photo_button.configure(text="Start Stream", command=stream)

    stream_link_button = Button("Copy Stream Link to Clipboard", copy_link_to_cb, 0.775, 0.55)

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)

    os.system(stream_command)
    sleep(1)
    take_photo_button.configure(text="End Stream", command=end_stream)
    mode_menu.disable()
    shutter_button_active = True

    def stream_loop():
        while True:
            if GPIO.input(26) == False:
                end_stream()
                sleep(1)
                break
            else:
                sleep(shutter_read_delay)
    
    threading.Thread(target=stream_loop).start()


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
    quality = "--quality " + choice.strip("%")
    choice = timer_menu.get_option()

    if choice == "0s":
        timer = ""
    else:
        timer = "--timeout " + str(int(choice.strip("s")) * 1000)
    
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
        preview_c = "-p 0,0,480,800"
    else:
        preview_c = "-p 35,192,400,250"

    preview_command = ("libcamera-still -t 0 " + preview_c + " " + rotation + " " + timer + " " + get_focus() + " --denoise cdn_off " + quality + " " + resolution + " " + shutter_speed + " " + gain.get_value() + " " + awbgains + " " + exposure_compensation.get_value() + " " + hdr + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + " &")
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
        sleep(1)
        take_photo_button.configure(text="Start Preview", command=preview)
        preview_active = False
        mode_menu.enable()

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)

    os.system(preview_command)
    sleep(1)
    take_photo_button.configure(text="Stop Preview", command=stop_preview)
    preview_active = True
    mode_menu.disable()
    shutter_button_active = True

    def preview_loop():
        while True:
            if GPIO.input(26) == False:
                stop_preview()
                sleep(1)
                break
            else:
                sleep(shutter_read_delay)

    threading.Thread(target=preview_loop).start()


def timelapse():
    global shutter_button_active
    
    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    choice = quality_menu.get_option()
    quality = "--quality " + choice.strip("%")
    
    choice = timer_menu.get_option()

    if choice == "0s":
        timer = ""
    else:
        timer = "--timeout " + str(int(choice.strip("s")) * 1000)
    
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
        preview = "-p 0,0,480,800"
    else:
        preview = "-p 35,192,400,250"
    
    if immediate_shutter_checkbox.get() == 1:
        immediate = "--immediate"
    else:
        immediate = ""

    date = strftime('%m-%d-%Y %H-%M-%S')
    timelapse_command = ("libcamera-still " + preview + " " + timer + " " + get_focus() + " " + rotation + " --viewfinder-width 2312 --viewfinder-height 1736 --denoise cdn_off " + quality + " " + get_resolution() + " " + immediate + " " + shutter_speed + " " + gain.get_value() + " " + awbgains + " " + exposure_compensation.get_value() + " " + hdr + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + " -o /home/pi/photos/'" + date + " Timelapse ")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", timelapse_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

    mode_menu.disable()
    shutter_button_active = True

    def stop_timelapse():
        global shutter_button_active, break_timelapse_loop
        os.system('pkill libcamera-still')
        break_timelapse_loop = True
        shutter_button_active = False
        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)
        sleep(1)
        mode_menu.enable()
        take_photo_button.configure(text="Start Timelapse", command=timelapse)

    sleep(1)
    take_photo_button.configure(text="Stop Timelapse", command=stop_timelapse)

    image_format_start, encode_format = get_image_format().split(" -")
    encode_format = " -" + encode_format

    def timelapse_loop():
        global break_timelapse_loop
        break_timelapse_loop = False
        timelapse_num = 1

        if flash_on_capture:
                GPIO.output(12, GPIO.HIGH)
        
        while True:
            os.system(timelapse_command + str(timelapse_num) + image_format_start + "'" + encode_format)
            timelapse_num += 1
        
            if break_timelapse_loop:
                break

    def timelapse_shutter_check():
        global break_timelapse_loop
        break_timelapse_loop = False

        while True:
            if GPIO.input(26) == False:
                stop_timelapse()
                sleep(1)
                break
            else:
                sleep(shutter_read_delay)
        
            if break_timelapse_loop:
                break
    
    timelapse_thread = threading.Thread(target=timelapse_loop)
    timelapse_thread.start()
    timelapse_shutter_thread = threading.Thread(target=timelapse_shutter_check)
    timelapse_shutter_thread.start()


def burst():
    global shutter_button_active

    choice = shutter_speed_menu.get_option()

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--shutter " + str(round(eval(choice) * 1000000)))

    if awb_blue_gain.get_value() == "" or awb_red_gain.get_value() == "":
        awbgains = ""
    else:
        awbgains = "--awbgains " + awb_red_gain.get_value().strip() + "," + awb_blue_gain.get_value().strip()

    rotation = "--rotation " + rotation_menu.get_option()

    if fullscreen_preview_checkbox.get() == 1:
        preview = "-p 0,0,480,800"
    else:
        preview = "-p 35,192,400,250"

    date = strftime('%m-%d-%Y %H-%M-%S')
    burst_command = ("libcamera-vid --codec mjpeg -t 0 --segment 1 -o /home/pi/photos/'" + date + " Burst %d.jpg' --framerate 30 --metering centre --denoise cdn_off " + preview + " " + rotation + " " + get_focus() + " " + get_resolution() + " " + shutter_speed + " " + awbgains + " " + gain.get_value() + " " + exposure_compensation.get_value() + " " + brightness.get_value() + " " + contrast.get_value() + " " + saturation.get_value() + " " + sharpness.get_value() + " " + calculate_digital_zoom() + "&")
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", burst_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)

    def stop_burst():
        global shutter_button_active
        os.system('pkill libcamera-vid')
        shutter_button_active = False
        if flash_on_capture:
                GPIO.output(12, GPIO.LOW)
        sleep(1)
        mode_menu.enable()
        take_photo_button.configure(text="Start", command=burst)

    if flash_on_capture:
        GPIO.output(12, GPIO.HIGH)

    os.system(burst_command)
    sleep(1)
    take_photo_button.configure(text="Stop", command=stop_burst)
    mode_menu.disable()
    shutter_button_active = True

    def burst_loop():
        while True:
            if GPIO.input(26) == False:
                stop_burst()
                sleep(1)
                break
            else:
                sleep(shutter_read_delay)

    threading.Thread(target=burst_loop).start()


def update(choice="", value=""):
    global last_mode
    
    if focus_menu.get_option() == "Manual":
        lens_position.enable("Lens Position")
    elif focus_menu.get_option() == "Fixed":
        lens_position.disable("Lens Position Fixed")
    else:
        lens_position.disable("Lens Position Auto")
    
    if awb_red_gain.get_value() == "":
        awb_blue_gain.enable("AWB Blue Gain Auto")
    if awb_blue_gain.get_value() == "":
        awb_red_gain.enable("AWB Red Gain Auto")
    
    if protocol_menu.get_option() == "RTSP":
        image_format_menu.disable("H.264")
    elif protocol_menu.get_option() == "TCP" or protocol_menu.get_option() == "UDP":
        image_format_menu.enable()
    
    if image_format_menu.get_option() == "MJPEG":
        quality_menu.enable()
    elif image_format_menu.get_option() == "H.264":
        quality_menu.disable("100%")
    
    if hdr_menu.get_option() == "On":
        resolution_menu.change_options(low_resolution_list)
        if resolution_menu.get_option() == resolution_default or resolution_menu.get_option() == "8K" or resolution_menu.get_option() == "48MP":
            resolution_menu.set_option(low_resolution_default)
    elif hdr_menu.get_option() == "Off" and mode_menu.get_option() == "Photo":
        resolution_menu.change_options(resolution_list)

    if mode_menu.get_option() == "Photo" and last_mode != "Photo":
        take_photo_button.configure(text="Take Photo", command=take_photo)
        resolution_menu.redef(resolution_default, resolution_list)
        shutter_speed_menu.redef(default_photo_shutter_speed, photo_shutter_speeds, "Shutter Speed")
        shutter_speed_menu.enable()
        quality_menu.enable()
        image_format_menu.redef("JPG", ["JPG", "PNG", "RAW + JPG"])
        image_format_menu.enable()
        timer_menu.enable()
        focus_menu.redef(default_photo_focus, photo_focus_list)
        protocol_menu.disable("None")
        hdr_menu.enable("Off")
        immediate_shutter_checkbox.configure(state="normal")
        last_mode = "Photo"

    elif mode_menu.get_option() == "Video" and last_mode != "Video":
        take_photo_button.configure(text="Take Video", command=take_video)
        resolution_menu.redef(default_video_resolution, video_resolution_list)
        shutter_speed_menu.redef(default_video_shutter_speed, video_shutter_speeds, "Shutter Speed")
        quality_menu.disable("100%")
        image_format_menu.disable("MP4")
        timer_menu.disable("0s")
        focus_menu.redef(default_video_focus, video_focus_list)
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Video"
    
    elif mode_menu.get_option() == "Stream" and last_mode != "Stream":
        take_photo_button.configure(text="Start Stream", command=stream)
        resolution_menu.redef(default_video_resolution, video_resolution_list)
        quality_menu.disable("100%")
        shutter_speed_menu.redef(default_video_shutter_speed, video_shutter_speeds, "Shutter Speed")
        image_format_menu.redef("H.264", ["H.264", "MJPEG"])
        image_format_menu.enable()
        timer_menu.disable("0s")
        focus_menu.redef(default_video_focus, video_focus_list)
        protocol_menu.enable("TCP")
        hdr_menu.disable("Off")
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Stream"
    
    elif mode_menu.get_option() == "Preview" and last_mode != "Preview":
        take_photo_button.configure(text="Start Preview", command=preview)
        resolution_menu.redef("4MP", ["4MP", "1080P"])
        shutter_speed_menu.redef(default_photo_shutter_speed, photo_shutter_speeds, "Shutter Speed")
        shutter_speed_menu.enable()
        quality_menu.disable()
        image_format_menu.set_option("None")
        image_format_menu.disable()
        timer_menu.disable("0s")
        focus_menu.redef(default_photo_focus, photo_focus_list)
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Preview"

    elif mode_menu.get_option() == "Timelapse" and last_mode != "Timelapse":
        take_photo_button.configure(text="Start Timelapse", command=timelapse)
        resolution_menu.redef(resolution_default, resolution_list)
        shutter_speed_menu.redef(default_photo_shutter_speed, photo_shutter_speeds, "Shutter Speed")
        shutter_speed_menu.enable()
        quality_menu.enable()
        image_format_menu.redef("JPG", ["JPG", "PNG", "RAW + JPG"])
        image_format_menu.enable()
        timer_menu.enable()
        focus_menu.redef(default_photo_focus, photo_focus_list)
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        immediate_shutter_checkbox.configure(state="normal")
        last_mode = "Timelapse"

    elif mode_menu.get_option() == "Burst" and last_mode != "Burst":
        take_photo_button.configure(text="Start", command=burst)
        resolution_menu.redef(low_resolution_default, low_resolution_list)
        shutter_speed_menu.redef(default_photo_shutter_speed, photo_shutter_speeds, "Shutter Speed")
        quality_menu.disable("100%")
        image_format_menu.disable("JPG")
        timer_menu.disable("0s")
        focus_menu.redef(default_video_focus, video_focus_list)
        protocol_menu.disable("None")
        hdr_menu.disable("Off")
        immediate_shutter_checkbox.configure(state="disabled")
        immediate_shutter_checkbox.deselect()
        last_mode = "Burst"
    
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


lens_position = Slider("Lens Position", "--lens-position", 0, 15, 0.1, 0.3, 1)
lens_position.disable("Lens Position Auto")

gain = Slider("Gain", "--gain", 0, 96, 0.3, 0.3, 0, auto=True) # Can mabye go up to 232
awb_red_gain = Slider("AWB Red Gain", "", 0, 5, 0.5, 0.3, 1, auto=True)
awb_blue_gain = Slider("AWB Blue Gain", "", 0, 5, 0.7, 0.3, 1, auto=True)
exposure_compensation = Slider("Exposure Compensation", "--ev", -25, 25, 0.9, 0.3, 0)
brightness = Slider("Brightness", "--brightness", -1, 1, 0.7, 0.4, 1)
contrast = Slider("Contrast", "--contrast", 0, 2, 0.9, 0.4, 1)
saturation = Slider("Saturation", "--saturation", 0, 2, 0.7, 0.5, 1)
sharpness = Slider("Sharpness", "--sharpness", 0, 2, 0.9, 0.5, 1)
digital_zoom = Slider("Digital Zoom", "", 1, 5, 0.9, 0.2, 0)

mode_menu = DropDownMenu("Mode", "Photo", 0.1, 0.1, ["Photo", "Video", "Stream", "Preview", "Timelapse", "Burst"])
resolution_menu = DropDownMenu("Resolution", resolution_default, 0.25, 0.1, resolution_list)
shutter_speed_menu = DropDownMenu("Shutter Speed", default_photo_shutter_speed, 0.4, 0.1, photo_shutter_speeds)
quality_menu = DropDownMenu("Quality", "100%", 0.55, 0.1, ["100%", "75%", "50%", "25%"])
image_format_menu = DropDownMenu("Format", "JPG", 0.7, 0.1, ["JPG", "PNG", "RAW + JPG"])
timer_menu = DropDownMenu("Timer", "0s", 0.85, 0.1, ["0s", "3s", "5s", "10s", "30s"])
focus_menu = DropDownMenu("Focus", default_photo_focus, 0.1, 0.2, photo_focus_list)
flash_menu = DropDownMenu("Flash", "Off", 0.25, 0.2, ["On Capture", "On", "Off"])
protocol_menu = DropDownMenu("Protocol", "None", 0.4, 0.2, ["TCP", "UDP", "RTSP"])
protocol_menu.disable()
rotation_menu = DropDownMenu("Rotation", "180", 0.55, 0.2, ["0", "180"])
hdr_menu = DropDownMenu("HDR", "Off", 0.7, 0.2, ["Off", "On"])

shutdown_button = customtkinter.CTkButton(master=app, text="Shutdown", command=shutdown)
shutdown_button.place(relx=0.7, rely=0.8, anchor=tkinter.CENTER)
camera_reset_button = customtkinter.CTkButton(master=app, text="Camera Reset", command=camera_reset)
camera_reset_button.place(relx=0.7, rely=0.75, anchor=tkinter.CENTER)
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

system_time_label = customtkinter.CTkLabel(master=app, text="System Time: ", justify=customtkinter.LEFT)
system_time_label.place(relx=0.675, rely=0.875, anchor=tkinter.CENTER)


def update_system_time():
    while True:
        system_time_label.configure(text="System Time: " + strftime("%m/%d/%Y %H:%M:%S"))
        sleep(1)
        if closing:
            break


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
            elif mode_menu.get_option() == "Timelapse":
                timelapse()
            elif mode_menu.get_option() == "Burst":
                burst()

        sleep(shutter_read_delay) #0.06

        if closing:
            break


threading.Thread(target=check_flash_and_shutter_button).start()
threading.Thread(target=update_system_time).start()

app.protocol("WM_DELETE_WINDOW", on_closing)
app.mainloop()
