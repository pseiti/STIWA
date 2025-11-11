import os
import random
import time
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.stats import norm
from tkinter import *
from tkVideoPlayer import TkinterVideo
from PIL import ImageTk, Image
from tkvideo import tkvideo
from queue import Queue
import threading
from src.haptic_core_serial import *
import exp1_stimuli as stim

"""
Further improved version: cleaner structure, safer resource handling,
better separation of concerns, improved naming, and clearer logic.
"""

# ---------------------------
# Haptics Setup
# ---------------------------

class HapticController:
    def __init__(self, ports, protocol_version="1.0"):
        self.ports = ports
        self.protocol_version = protocol_version
        self.stop_event = threading.Event()

        self.input_queues = {name: Queue() for name in ports}
        self.output_queues = {name: Queue() for name in ports}
        self.threads = []

        for name, port in ports.items():
            thread = threading.Thread(
                target=process_serial_data,
                args=(port, protocol_version, self.stop_event,
                      self.input_queues[name], self.output_queues[name]),
                daemon=True
            )
            self.threads.append(thread)
            thread.start()

    def read_angle(self, device="hcc1"):
        return get_register(
            "report_encoder_angle",
            self.output_queues[device],
            self.input_queues[device]
        )

    def set_tick_angle(self, angle, device="hcc1"):
        set_register("tick_angle_cw", angle, self.output_queues[device])

    def stop(self):
        self.stop_event.set()
        for t in self.threads:
            t.join(timeout=1)


# Initialize haptic system
haptics = HapticController({"hcc1": "COM3"})
haptics.set_tick_angle(3)
INIT_ANGLE = haptics.read_angle()


# ---------------------------
# Helper Functions
# ---------------------------

class HelperFunctions:
    def __init__(self, font="Arial", font_size=16, haptics=None):
        self.font = font
        self.font_size = font_size
        self.haptics = haptics

    def open_text_window(self, parent, title, text, geometry):
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)
        Label(window, text=text, font=(self.font, self.font_size)).pack(padx=10, pady=10)

    def open_practice_window(self, parent, title, geometry):
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)
        # filepath = "C:/Users/47_nb_admin/Documents/GitHub/STIWA/StimRespComp/stimuli/vid1.mp4"
        player = TkinterVideo(window)
        player.load("stimuli/vid1.mp4")
        player.play()

    def application_tick(self, init_angle):
        if not self.haptics:
            return None
        current = self.haptics.read_angle()
        diff = current - init_angle
        print(f"Current angle: {current}, Diff: {diff}")
        return current, diff

    def stop_threads(self):
        if self.haptics:
            self.haptics.stop()


# ---------------------------
# Main GUI
# ---------------------------

DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT, haptics=haptics)

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

Label(
    root,
    text="""
Please click on the instructions button
and read the information carefully!
""",
    font=DEFAULT_FONT
).pack(pady=10)


def quit_app():
    helper.application_tick(INIT_ANGLE)
    helper.stop_threads()
    root.quit()


Button(
    root,
    text="Instruction",
    font=DEFAULT_FONT,
    command=lambda: helper.open_text_window(
        root, "Instruction", "...", "600x400+500+50")
).pack(pady=10)

Button(
    root,
    text="Start Practice",
    font=DEFAULT_FONT,
    command=lambda: helper.open_practice_window(
        root, "Practice Session", "600x400+500+50")
).pack(pady=10)

Button(root, text="Close", font=DEFAULT_FONT, command=quit_app).pack(pady=10)

root.mainloop()
