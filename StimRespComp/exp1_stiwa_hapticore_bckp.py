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
from queue import Queue
import threading
from src.haptic_core_serial import *
import exp1_stimuli


# ---------------------------
# Global session variables
# ---------------------------

cur_set_of_stimuli = []
x = 0   # index for selecting videos


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
    def __init__(self, font="Arial", font_size=16, pad_x=10, pad_y=10, haptics=None):
        self.font = font
        self.font_size = font_size
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.haptics = haptics
        self.monitor_thread = None
        self.stop_event = None

    # --- Core utilities ---
    def application_tick(self, INIT_ANGLE):
        if not self.haptics:
            return None, None
        current = self.haptics.read_angle()
        diff = current - INIT_ANGLE
        # print(f"Current angle: {current}, Diff: {diff}")
        return current, diff

    # --- GUI helpers ---

    def open_text_window(self, parent, title, text, geometry):
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)
        Label(
            window,
            text=text,
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT,
        ).pack(padx=self.pad_x, pady=self.pad_y)

    def fixation_cross(self, window):

        def show_label(lbl):
            lbl.pack()

        def remove_label(lbl):
            lbl.destroy()

        label = Label(window, text="\n\n+", font=("Arial", 40))
        window.after(1000, show_label, label)
        window.after(2000, remove_label, label)

    # --- Corrected monitor_haptic_input ---
    def monitor_haptic_input(self, player, init_angle_local, stop_event, window, 
        condition, time_vidStarted):
        global INIT_ANGLE, x, cur_set_of_stimuli, df

        while not stop_event.is_set():
            angle, diff = self.application_tick(init_angle_local)
            if angle is None:
                time.sleep(0.05)
                continue

            if abs(diff) > 10:
                RT = time.time() - time_vidStarted
                stop_event.set()

                player.destroy()

                def update_init_angle():
                    global INIT_ANGLE, x
                    INIT_ANGLE = self.haptics.read_angle()
                    x += 1

                update_init_angle()

                target_present = True if condition[2]=="P" else False
                scroll_forward = True if diff > 0 else False
                scrolling_direction = "Fwd" if diff > 0 else "Bwd"
                fwd_means_present = True # if condition[] # IAS

                resp_cat = self.sdt_resp_cat(target_present, scroll_forward, fwd_means_present)
                
                # columns = ["code","condition","scrolling_direction","sdt_resp_cat","RT"]
                df.loc[len(df.index)] = [cur_code, condition, scrolling_direction, resp_cat, RT]
                print(df)

                if x >= n_vids_prac:
                    Label(
                        window,
                        text="\n\nThank you for your efforts and your time.",
                        font=(self.font, self.font_size),
                        wraplength=500,
                        justify=LEFT,
                    ).pack(padx=self.pad_x, pady=self.pad_y)

                else:
                    self.fixation_cross(window)
                    window.after(3000, self.playVideo, window,
                                 cur_set_of_stimuli[x].get("clip"), x, condition)

            time.sleep(0.05)

    def sdt_resp_cat(self, target_present, scroll_forward, fwd_means_present):
        resp_cat = None
        if fwd_means_present:
            if target_present:
                resp_cat="Hit" if scroll_forward else "Miss"
            else:
                resp_cat="FA" if scroll_forward else "CR"
        else:
            if target_present:
                resp_cat="Miss" if scroll_forward else "Hit"
            else:
                resp_cat="CR" if scroll_forward else "FA"

        return resp_cat

    def open_session_window(self, parent, title, geometry, part_of_session):
        global cur_set_of_stimuli, x
        x = 0

        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)

        if part_of_session == "practice":
            cur_set_of_stimuli = exp1_stimuli.stimuli_practice_ordered
        elif part_of_session == "test":
            cur_set_of_stimuli = exp1_stimuli.stimuli_test

        self.fixation_cross(window)
        condition = cur_set_of_stimuli[x].get("condi")
        condition = zooming_direction + condition
        window.after(3000, self.playVideo, window,
                     cur_set_of_stimuli[x].get("clip"), x, condition)

    def playVideo(self, window, vid_x, x, condition):
        player = TkinterVideo(window)
        player.load(vid_x)
        player.pack(expand=True, fill="both")
        player.play()
        
        time_vidStarted = time.time()

        self.stop_event = threading.Event()
        self.monitor_thread = threading.Thread(
            target=self.monitor_haptic_input,
            args=(player, INIT_ANGLE, self.stop_event, window, condition, time_vidStarted),
            daemon=True
        )
        self.monitor_thread.start()

        def on_close():
            global INIT_ANGLE
            INIT_ANGLE = self.haptics.read_angle()
            self.stop_event.set()
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

    def stop_threads(self):
        if self.stop_event:
            self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        if self.haptics:
            self.haptics.stop()


# ---------------------------
# Main GUI
# ---------------------------

n_vids_prac = 3
DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT, haptics=haptics)
columns = ["code","condition","scrolling_direction","sdt_resp_cat","RT"]
df = pd.DataFrame(columns=columns)
cur_code = "pcs"

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

Label(
    root,
    text="""Please click on the instructions button
and read the information carefully!
""",
    font=DEFAULT_FONT
).pack(pady=20)

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
    command=lambda: helper.open_session_window(
        root, "Practice Session", "600x400+500+50", "practice")
).pack(pady=10)

Button(
    root,
    text="Close",
    font=DEFAULT_FONT,
    command=lambda: (helper.stop_threads(), root.destroy())
).pack(pady=10)

root.mainloop()
