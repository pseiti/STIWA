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
from pynput import mouse  # <-- needed for mocking
import exp1_stimuli


# ---------------------------
# Mouse-Based Haptic Mock
# ---------------------------

class MouseHapticMock:
    def __init__(self):
        self.angle = 0
        self.tick_angle = 3
        self.listener = mouse.Listener(on_scroll=self._on_scroll)
        self.listener.start()

    def _on_scroll(self, x, y, dx, dy):
        self.angle += dy * self.tick_angle

    def read_angle(self, device="hcc1"):
        return self.angle

    def set_tick_angle(self, angle, device="hcc1"):
        self.tick_angle = angle

    def stop(self):
        self.listener.stop()


# Initialize mock haptic system
haptics = MouseHapticMock()
haptics.set_tick_angle(3)


# ---------------------------
# Helper Functions
# ---------------------------

class HelperFunctions:
    def __init__(self, font="Arial", font_size=16, pad_x=10, pad_y=10,
                 ms_fixcross=1000, haptics=None):

        self.font = font
        self.font_size = font_size
        self.pad_x = pad_x
        self.pad_y = pad_y
        self.ms_fixcross = ms_fixcross
        self.haptics = haptics

        # Former globals → instance attributes
        self.cur_set_of_stimuli = []
        self.trial_index = 0
        self.session_window = None
        self.label_hit_the_spacebar = None
        self.init_angle = self.haptics.read_angle() if haptics else 0

        # threading control
        self.monitor_thread = None
        self.stop_event = None

    # --- GUI helpers ---

    def open_text_window(self, parent, title, text, geometry):
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)
        Label(window,
              text=text,
              font=(self.font, self.font_size),
              wraplength=500,
              justify=LEFT).pack(padx=self.pad_x, pady=self.pad_y)

    def open_session_window(self, parent, title, geometry, part_of_session):
        self.trial_index = 0

        self.session_window = Toplevel(parent)
        self.session_window.title(title)
        self.session_window.geometry(geometry)

        if part_of_session == "practice":
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_practice
        elif part_of_session == "test":
            self.cur_set_of_stimuli = exp1_stimuli.stimuli_test

        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT,
        )
        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)

        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    def bind_spacebar(self):
        self.label_hit_the_spacebar = Label(
            self.session_window,
            text="Hit the space bar to start the trial.",
            font=(self.font, self.font_size),
            wraplength=500,
            justify=LEFT
        )
        self.label_hit_the_spacebar.pack(padx=self.pad_x, pady=self.pad_y)
        self.session_window.bind("<space>", self.starttrial_by_spacebar)

    def starttrial_by_spacebar(self, event):
        self.label_hit_the_spacebar.destroy()
        self.session_window.unbind("<space>")
        self.fixation_cross()

        condition = self.cur_set_of_stimuli[self.trial_index].get("condi")
        print(self.cur_set_of_stimuli[self.trial_index])
        condition = zooming_direction + condition

        self.session_window.after(
            self.ms_fixcross * 3,
            self.playVideo,
            self.cur_set_of_stimuli[self.trial_index].get("clip"),
            condition
        )

    def fixation_cross(self):
        def show_label(lbl):
            lbl.pack()

        def remove_label(lbl):
            lbl.destroy()

        label_fixation_cross = Label(self.session_window, text="\n\n+", font=("Arial", 40))
        self.session_window.after(self.ms_fixcross, show_label, label_fixation_cross)
        self.session_window.after(self.ms_fixcross * 2, remove_label, label_fixation_cross)

    def playVideo(self, vid_x, condition):
        player = TkinterVideo(self.session_window)
        player.load(vid_x)
        player.pack(expand=True, fill="both")
        player.play()

        time_vidStarted = time.time()

        self.stop_event = threading.Event()
        self.monitor_thread = threading.Thread(
            target=self.monitor_haptic_input,
            args=(player,
                  self.init_angle,
                  self.stop_event,
                  condition,
                  time_vidStarted),
            daemon=True
        )
        self.monitor_thread.start()

        def on_close():
            self.init_angle = self.haptics.read_angle()
            self.stop_event.set()
            self.session_window.destroy()

        self.session_window.protocol("WM_DELETE_WINDOW", on_close)

    # --- Core utilities ---
    def application_tick(self, init_angle):
        if not self.haptics:
            return None, None
        current = self.haptics.read_angle()
        diff = current - init_angle
        return current, diff

    def monitor_haptic_input(self, player, init_angle_local, stop_event,
                             condition, time_vidStarted):
        global df, cur_code, n_vids_prac

        while not stop_event.is_set():
            angle, diff = self.application_tick(init_angle_local)
            if angle is None:
                time.sleep(0.05)
                continue

            # Mouse-triggered response
            if abs(diff) > 2:
                RT = time.time() - time_vidStarted
                stop_event.set()
                player.destroy()

                # update angle and trial index
                self.init_angle = self.haptics.read_angle()
                self.trial_index += 1

                target_present = True if condition[2] == "P" else False
                scroll_forward = True if diff > 0 else False
                scrolling_direction = "Fwd" if diff > 0 else "Bwd"
                fwd_means_present = True

                resp_cat = self.sdt_resp_cat(
                    target_present, scroll_forward, fwd_means_present
                )

                df.loc[len(df.index)] = [
                    cur_code, condition, scrolling_direction, resp_cat, RT
                ]
                print(df)

                if self.trial_index >= n_vids_prac:
                    Label(
                        self.session_window,
                        text="\n\nThank you for your efforts and your time.",
                        font=(self.font, self.font_size),
                        wraplength=500,
                        justify=LEFT,
                    ).pack(padx=self.pad_x, pady=self.pad_y)

                    df.to_csv(cur_code + "_SRC_exp12.csv")

                else:
                    self.session_window.after(
                        self.ms_fixcross,
                        self.bind_spacebar
                    )

            time.sleep(0.05)

    def stop_threads(self):
        if self.stop_event:
            self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        if self.haptics:
            self.haptics.stop()

    def sdt_resp_cat(self, target_present, scroll_forward, fwd_means_present):
        if fwd_means_present:
            if target_present:
                return "Hit" if scroll_forward else "Miss"
            else:
                return "FA" if scroll_forward else "CR"
        else:
            if target_present:
                return "Miss" if scroll_forward else "Hit"
            else:
                return "CR" if scroll_forward else "FA"

    def performance_measures(self, df):
        nHits = len(df[df['sdt_resp_cat'] == 'Hit'])
        nMiss = len(df[df['sdt_resp_cat'] == 'Miss'])
        nCR = len(df[df['sdt_resp_cat'] == 'CR'])
        nFA = len(df[df['sdt_resp_cat'] == 'FA'])

        if nHits == 0:
            hitRate = 1 / np.sqrt(400)
        else:
            hitRate = nHits / (nHits + nMiss)
        if hitRate == 1:
            hitRate = 1 - 1 / np.sqrt(400)

        if nFA == 0:
            faRate = 1 - 1 / np.sqrt(400)
        else:
            faRate = nFA / (nCR + nFA)
        if faRate == 1:
            faRate = 1 - 1 / np.sqrt(400)

        dPrime = st.norm.ppf(hitRate) - st.norm.ppf(faRate)
        percentError = hitRate - faRate
        return [percentError, hitRate, faRate, dPrime]


# ---------------------------
# Main GUI
# ---------------------------
n_vids_prac = 10
DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT, haptics=haptics)

columns = ["code", "condition", "scrolling_direction", "sdt_resp_cat", "RT"]
df = pd.DataFrame(columns=columns)

cur_code = "pcs"
zooming_direction = "Z"

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
