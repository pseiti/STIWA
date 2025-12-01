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
import exp1_stimuli


"""
Experiment GUI – Hardware-free version.
All Hapticore functionality is replaced with mouse-based movement detection.
"""


# ======================================================================
#  MOCK HAPTICS (MOUSE-BASED INPUT)
# ======================================================================

class MockHaptics:
    """Simulates encoder angle changes using horizontal mouse movement."""
    def __init__(self, root):
        self.root = root
        self.last_x = None
        self.current_diff = 0
        root.bind("<Motion>", self._on_mouse_move)

    def _on_mouse_move(self, event):
        if self.last_x is None:
            self.last_x = event.x
            return
        self.current_diff = event.x - self.last_x
        self.last_x = event.x

    def read_angle(self):
        """Return dummy angle = None, and real diff = mouse Δx."""
        return None, self.current_diff

    def set_tick_angle(self, *args, **kwargs):
        pass

    def stop(self):
        pass


INIT_ANGLE = 0  # Not used in mouse-control mode


# ======================================================================
#  HELPER FUNCTIONS
# ======================================================================

class HelperFunctions:
    def __init__(self, font="Arial", font_size=16, haptics=None):
        self.font = font
        self.font_size = font_size
        self.haptics = haptics
        self.monitor_thread = None
        self.stop_event = None

    # --- CORE INPUT PROCESSING ---
    def application_tick(self, init_angle):
        """Read mouse movement instead of encoder angle."""
        if not self.haptics:
            return None, None

        angle, diff = self.haptics.read_angle()
        print(f"Mouse Δx: {diff}")
        return angle, diff

    # --- GUI WINDOWS ---
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
        ).pack(padx=10, pady=10)

    # --- HAPTIC/MOUSE MONITORING LOOP ---
    def monitor_haptic_input(self, player, init_angle, stop_event):
        """Monitor mouse movement and pause video if threshold crossed."""
        while not stop_event.is_set():
            angle, diff = self.application_tick(init_angle)

            if diff is None:
                continue

            # movement threshold
            if abs(diff) > 10:
                print("Movement threshold exceeded — pausing video.")
                player.pause()
                stop_event.set()

            time.sleep(0.05)

    # --- SESSION WINDOW ---
    def open_session_window(self, parent, title, geometry, part_of_session):
        global cur_set_of_stimuli

        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)

        if part_of_session == "practice":
            cur_set_of_stimuli = exp1_stimuli.stimuli_practice_ordered
        elif part_of_session == "test":
            cur_set_of_stimuli = exp1_stimuli.stimuli_test

        # Here you will later call video display
        # For now the screen only opens.

    # --- VIDEO PLAYER ---
    def playVideo(self, window, vid_x):
        player = TkinterVideo(window)
        player.load(vid_x)
        player.pack(expand=True, fill="both")
        player.play()

        # start monitoring thread
        self.stop_event = threading.Event()
        self.monitor_thread = threading.Thread(
            target=self.monitor_haptic_input,
            args=(player, INIT_ANGLE, self.stop_event),
            daemon=True
        )
        self.monitor_thread.start()

        def on_close():
            self.stop_event.set()
            window.destroy()

        window.protocol("WM_DELETE_WINDOW", on_close)

    def trial_fx(self, vid_x):
        self.playVideo(vid_x)

    # --- SHUTDOWN ---
    def stop_threads(self):
        if self.stop_event:
            self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1)
        if self.haptics:
            self.haptics.stop()


# ======================================================================
#  MAIN GUI
# ======================================================================

DEFAULT_FONT = ("Arial", 16)

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

# initialize mouse-based mock haptics
mock_haptics = MockHaptics(root)
helper = HelperFunctions(*DEFAULT_FONT, haptics=mock_haptics)


def quit_app():
    helper.stop_threads()
    root.destroy()


Label(
    root,
    text="""
Please click on the instructions button
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
    command=quit_app
).pack(pady=10)

root.mainloop()
