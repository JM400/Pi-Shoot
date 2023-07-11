version = "v1.0 May/7/2023"

# Import modules
from time import strftime
from time import sleep
from PIL import Image
import customtkinter
import threading
import paramiko
import tkinter
import sys
import os


# Set theme
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("green")
customtkinter.set_widget_scaling(1)
customtkinter.set_window_scaling(1)


# Setup window
app = customtkinter.CTk()
app.geometry("1024, 768")
app.minsize(1024, 768)
app.maxsize(1920, 1080)
app.title("64MP Camera Controller                " + version)


# Default Values
timer = ""
focus = "--autofocus-on-capture"
quality = "--quality 100"
resolution = "--width 9152 --height 6944"
maxsize_option = 1
shutter_speed = ""
gain = ""
image_format = ".jpg"
awbgains = ""
ssh = False
stop_checking_for_photo = False


# Default Image
try:
    image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    image = customtkinter.CTkImage(Image.open(os.path.join(image_path, "Start Photo.png")), size=(500,375))
    image_label = customtkinter.CTkLabel(master=app, text="", image=image)
    image_label.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)
except:
    image_label = customtkinter.CTkLabel(master=app, text="")
    image_label.place(relx=0.3, rely=0.6, anchor=tkinter.CENTER)


def resolution_optionmenu_callback(choice):
    global resolution, maxsize_option

    if choice == "64MP":
        resolution = "--width 9152 --height 6944"
        maxsize_option = 1
    elif choice == "16MP":
        resolution = "--width 4624 --height 3472"
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


def shutter_speed_optionmenu_callback(choice):
    global shutter_speed

    if choice == "Auto":
        shutter_speed = ""
    else:
        shutter_speed = ("--immediate --shutter " + str(round(eval(choice) * 1000000)))


def gain_optionmenu_callback(choice):
    global gain

    if choice == "Auto":
        gain = ""
    else:
        gain = "--gain " + choice


def quality_optionmenu_callback(choice):
    global quality

    if choice == "100%":
        quality = "--quality 100"
    elif choice == "75%":
        quality = "--quality 75"
    elif choice == "50%":
        quality = "--quality 50"
    elif choice == "25%":
        quality = "--quality 25"


def format_optionmenu_callback(choice):
    global image_format

    if choice == "JPG":
        image_format = ".jpg"
    elif choice == "PNG":
        image_format = ".png"
    elif choice == "RAW 10":
        image_format = ".raw10"


def timer_optionmenu_callback(choice):
    global timer

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


def focus_optionmenu_callback(choice):
    global focus

    if choice == "Manual":
        optionmenu_8.configure(state="normal")
        optionmenu_8.set("Position 6")
        focus = "--lens-position 6"
    else:
        optionmenu_8.configure(state="disabled")
        optionmenu_8.set("Auto")
    
    if choice == "Autofocus":
        focus = "--autofocus-mode auto"
    elif choice == "Autofocus on Capture":
        focus = "--autofocus-on-capture"
    elif choice == "Continuous Autofocus":
        focus = "--autofocus-mode continuous"


def lens_position_optionmenu_callback(choice):
    global focus

    if choice == "Position 1":
        focus = "--lens-position 1"
    elif choice == "Position 2":
        focus = "--lens-position 2"
    elif choice == "Position 3":
        focus = "--lens-position 3"
    elif choice == "Position 4":
        focus = "--lens-position 4"
    elif choice == "Position 5":
        focus = "--lens-position 5"
    elif choice == "Position 6":
        focus = "--lens-position 6"
    elif choice == "Position 7":
        focus = "--lens-position 7"
    elif choice == "Position 8":
        focus = "--lens-position 8"
    elif choice == "Position 9":
        focus = "--lens-position 9"
    elif choice == "Position 10":
        focus = "--lens-position 10"
    elif choice == "Position 11":
        focus = "--lens-position 11"
    elif choice == "Position 12":
        focus = "--lens-position 12"


def awbgains_optionmenu_callback(choice):
    global awbgains

    if choice == "Auto":
        awbgains = ""
    elif choice == "1.0,1.0":
        awbgains = "--awbgains 1.0,1.0"
    elif choice == "1.5,2.0":
        awbgains = "--awbgains 1.5,2.0"


def flash_optionmenu_callback(choice):
    print("optionmenu dropdown clicked:", choice)


def shutdown():
    if ssh:
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command('sudo shutdown now')
        client.close()
        sleep(1)

    sys.exit()


def disconnect_ssh():
    global ssh, stop_checking_for_photo

    sftp.close()
    client.close()
    sleep(1)
    ssh_label.configure(text="Disconnected")
    take_photo_button.configure(state="normal")
    connect_ssh_button.configure(text="Connect SSH", command=connect_ssh)
    stop_checking_for_photo = True
    ssh = False

def connect_ssh():
    global client, sftp, ssh, stop_checking_for_photo
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.load_system_host_keys()
        client.connect(address_entry.get(), username= username_entry.get(), password= password_entry.get())
        sleep(1)

        transport = paramiko.Transport((address_entry.get(), 22))
        transport.connect(username = username_entry.get(), password = password_entry.get())

        sftp = paramiko.SFTPClient.from_transport(transport)

        ssh_label.configure(text="Connected!")
        connect_ssh_button.configure(text="Disconnect SSH", command=disconnect_ssh)
        stop_checking_for_photo = False
        ssh = True
    
    except:
        ssh = False
        stop_checking_for_photo = True
        ssh_label.configure(text="Connection Failed.")


def take_photo():
    date = strftime('%m-%d-%Y %H-%M-%S')
    photo_command = ("libcamera-still -n --rotation 180 " + timer + " " + focus + " --denoise cdn_off " + quality + " " + resolution + " " + shutter_speed + " " + gain + " " + awbgains + " -o /home/pi/photos/'" + date + "'" + image_format)
    command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
    command_textbox.insert("0.0", photo_command)
    command_textbox.configure(state="disabled")
    command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)
    

    if ssh:
        ssh_stdin, ssh_stdout, ssh_stderr = client.exec_command(photo_command)
        sleep(1)
        take_photo_button.configure(state="disabled")

        def check_for_photo():
            date_c = date
            image_format_c = image_format

            if maxsize_option == 1:
                maxsize = (500, 375)
            elif maxsize_option == 2:
                maxsize = (500, 281)

            while True:
                if stop_checking_for_photo:
                    break
                else:
                    try:
                        photo = sftp.open(("/home/pi/photos/" + date_c + image_format_c), "r")
                        image = customtkinter.CTkImage(Image.open(photo), size=(maxsize))
                        image_label.configure(image=image)
                        photo.close()
                        take_photo_button.configure(state="normal")
                        break
                    except:
                        sleep(1)

        threading.Thread(target=check_for_photo).start()


label_1 = customtkinter.CTkLabel(master=app, text="Resolution", justify=customtkinter.LEFT)
label_1.place(relx=0.1, rely=0.05, anchor=tkinter.CENTER)
optionmenu_1 = customtkinter.CTkOptionMenu(app, values=["64MP", "16MP", "4MP", "8K", "4K", "1080P"], command=resolution_optionmenu_callback)
optionmenu_1.set("64MP")
optionmenu_1.place(relx=0.1, rely=0.1, anchor=tkinter.CENTER)

label_2 = customtkinter.CTkLabel(master=app, text="Shutter Speed", justify=customtkinter.LEFT)
label_2.place(relx=0.25, rely=0.05, anchor=tkinter.CENTER)
optionmenu_2 = customtkinter.CTkOptionMenu(app, values=["Auto", "420", "360", "300", "240", "180", "120", "60", "30", "15", "1", "1/15", "1/30", "1/60", "1/120", "1/180", "1/240", "1/300", "1/360", "1/420", "1/1000", "1/2000"], command=shutter_speed_optionmenu_callback)
optionmenu_2.set("Auto")
optionmenu_2.place(relx=0.25, rely=0.1, anchor=tkinter.CENTER)

label_3 = customtkinter.CTkLabel(master=app, text="Gain", justify=customtkinter.LEFT)
label_3.place(relx=0.4, rely=0.05, anchor=tkinter.CENTER)
optionmenu_3 = customtkinter.CTkOptionMenu(app, values=["Auto", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"], command=gain_optionmenu_callback)
optionmenu_3.set("Auto")
optionmenu_3.place(relx=0.4, rely=0.1, anchor=tkinter.CENTER)

label_4 = customtkinter.CTkLabel(master=app, text="Quality", justify=customtkinter.LEFT)
label_4.place(relx=0.55, rely=0.05, anchor=tkinter.CENTER)
optionmenu_4 = customtkinter.CTkOptionMenu(app, values=["100%", "75%", "50%", "25%"], command=quality_optionmenu_callback)
optionmenu_4.set("100%")
optionmenu_4.place(relx=0.55, rely=0.1, anchor=tkinter.CENTER)

label_5 = customtkinter.CTkLabel(master=app, text="Format", justify=customtkinter.LEFT)
label_5.place(relx=0.7, rely=0.05, anchor=tkinter.CENTER)
optionmenu_5 = customtkinter.CTkOptionMenu(app, values=["JPG", "PNG", "RAW 10"], command=format_optionmenu_callback)
optionmenu_5.set("JPG")
optionmenu_5.place(relx=0.7, rely=0.1, anchor=tkinter.CENTER)

label_6 = customtkinter.CTkLabel(master=app, text="Timer", justify=customtkinter.LEFT)
label_6.place(relx=0.85, rely=0.05, anchor=tkinter.CENTER)
optionmenu_6 = customtkinter.CTkOptionMenu(app, values=["0s", "3s", "5s", "10s", "30s"], command=timer_optionmenu_callback)
optionmenu_6.set("0s")
optionmenu_6.place(relx=0.85, rely=0.1, anchor=tkinter.CENTER)

label_7 = customtkinter.CTkLabel(master=app, text="Focus", justify=customtkinter.LEFT)
label_7.place(relx=0.1, rely=0.15, anchor=tkinter.CENTER)
optionmenu_7 = customtkinter.CTkOptionMenu(app, values=["Autofocus", "Autofocus on Capture", "Manual", "Continuous Autofocus"], command=focus_optionmenu_callback)
optionmenu_7.set("Autofocus on Capture")
optionmenu_7.place(relx=0.1, rely=0.2, anchor=tkinter.CENTER)

label_8 = customtkinter.CTkLabel(master=app, text="Lens Position", justify=customtkinter.LEFT)
label_8.place(relx=0.25, rely=0.15, anchor=tkinter.CENTER)
optionmenu_8 = customtkinter.CTkOptionMenu(app, values=["Position 12", "Position 11", "Position 10", "Position 9", "Position 8", "Position 7", "Position 6", "Position 5", "Position 4", "Position 3", "Position 2", "Position 1",], command=lens_position_optionmenu_callback)
optionmenu_8.set("Auto")
optionmenu_8.configure(state="disabled")
optionmenu_8.place(relx=0.25, rely=0.2, anchor=tkinter.CENTER)

label_9 = customtkinter.CTkLabel(master=app, text="AWB Gains", justify=customtkinter.LEFT)
label_9.place(relx=0.4, rely=0.15, anchor=tkinter.CENTER)
optionmenu_9 = customtkinter.CTkOptionMenu(app, values=["Auto", "1.0,1.0", "1.5,2.0"], command=awbgains_optionmenu_callback)
optionmenu_9.set("Auto")
optionmenu_9.place(relx=0.4, rely=0.2, anchor=tkinter.CENTER)

label_10 = customtkinter.CTkLabel(master=app, text="Flash", justify=customtkinter.LEFT)
label_10.place(relx=0.55, rely=0.15, anchor=tkinter.CENTER)
optionmenu_10 = customtkinter.CTkOptionMenu(app, values=["On Capture", "On", "Off"], command=flash_optionmenu_callback)
optionmenu_10.set("Off")
optionmenu_10.configure(state="disabled")
optionmenu_10.place(relx=0.55, rely=0.2, anchor=tkinter.CENTER)

address_entry = customtkinter.CTkEntry(app, placeholder_text="Camera Address")
address_entry.place(relx=0.7, rely=0.6, anchor=tkinter.CENTER)
username_entry = customtkinter.CTkEntry(app, placeholder_text="Username")
username_entry.place(relx=0.7, rely=0.65, anchor=tkinter.CENTER)
password_entry = customtkinter.CTkEntry(app, placeholder_text="Password", show="*")
password_entry.place(relx=0.7, rely=0.7, anchor=tkinter.CENTER)

shutdown_button = customtkinter.CTkButton(master=app, text="Shutdown - Exit", command=shutdown)
shutdown_button.place(relx=0.7, rely=0.8, anchor=tkinter.CENTER)
connect_ssh_button = customtkinter.CTkButton(master=app, text="Connect SSH", command=connect_ssh)
connect_ssh_button.place(relx=0.7, rely=0.75, anchor=tkinter.CENTER)
take_photo_button = customtkinter.CTkButton(master=app, text="Take Photo", command=take_photo)
take_photo_button.place(relx=0.85, rely=0.6, anchor=tkinter.CENTER)

ssh_label = customtkinter.CTkLabel(master=app, text="", justify=customtkinter.LEFT)
ssh_label.place(relx=0.7, rely=0.85, anchor=tkinter.CENTER)

command_textbox = customtkinter.CTkTextbox(master=app, width=140, height=140)
command_textbox.insert("0.0", "")
command_textbox.configure(state="disabled")
command_textbox.place(relx=0.85, rely=0.725, anchor=tkinter.CENTER)


app.mainloop()
