import RPi.GPIO as GPIO
import paho.mqtt.client as mqtt
import time
import subprocess
import sys
import tkinter as tk

# GPIO pins
FAN_PIN = 18

# MQTT settings
MQTT_BROKER = "mqtt-dashboard.com"
MQTT_CO_TOPIC = "co_level"

GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PIN, GPIO.OUT)

co_levels = []
average_co = 0

def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT Broker with result code " + str(rc))
    client.subscribe(MQTT_CO_TOPIC)

def on_message(client, userdata, msg):
    global co_levels, average_co
    if msg.topic == MQTT_CO_TOPIC:
        co_level = int(msg.payload)
        co_levels.append(co_level)
        if len(co_levels) > 10:
            co_levels.pop(0)  # Keep the last 10 readings
        average_co = sum(co_levels) / len(co_levels)
        print("CO Level: " + str(co_level))
        
        # Check CO level and control the fan
        if co_level > 500:
            GPIO.output(FAN_PIN, GPIO.HIGH)
        else:
            GPIO.output(FAN_PIN, GPIO.LOW)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, 1883, 60)

def restart_program():
    python = sys.executable
    subprocess.Popen([python] + sys.argv)

def update_gui():
    average_label.config(text="Average CO Level: {:.2f}".format(average_co))
    
    if co_levels:  # Check if the list is not empty
        co_level_label.config(text="CO Level: " + str(co_levels[-1]))
    
    fan_status = "On" if GPIO.input(FAN_PIN) == GPIO.HIGH else "Off"
    fan_status_label.config(text="Fan Status: " + fan_status)
    
    root.after(1000, update_gui)

try:
    client.loop_start()

    root = tk.Tk()
    root.title("CO Level Monitor")

    average_label = tk.Label(root, text="Average CO Level: 0.00", font=("Arial", 16))
    average_label.pack(pady=10)
    
    co_level_label = tk.Label(root, text="CO Level: 0", font=("Arial", 16))
    co_level_label.pack(pady=10)

    fan_status_label = tk.Label(root, text="Fan Status: Off", font=("Arial", 16))
    fan_status_label.pack(pady=10)

    update_gui()

    root.mainloop()

except KeyboardInterrupt:
    GPIO.cleanup()
    client.loop_stop()
    restart_program()
