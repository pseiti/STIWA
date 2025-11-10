import os
import random
import time
import numpy as np
import pandas as pd
import scipy.stats as st
from scipy.stats import norm
from tkinter import *
from PIL import ImageTk, Image
from tkvideo import tkvideo
import exp1_stimuli as stim


class HelperFunctions:
    """GUI helper functions for opening additional windows."""

    def __init__(self, font="Arial", font_size=16):
        self.font = font
        self.font_size = font_size

    def open_text_window(self, parent, title, text, geometry):
        """Open a simple popup window containing text."""
        window = Toplevel(parent)
        window.title(title)
        window.geometry(geometry)

        label = Label(window, text=text, font=(self.font, self.font_size))
        label.pack(padx=10, pady=10)
    
    def open_practice_window(self, parent, title, geometry):
    	window = Toplevel(parent)
    	window.title(title)
    	window.geometry(geometry)
    	vid_player = tkvideo(master=window)
    	vid_player.pack(expand=True, fill="both")

class MainFunctions:
    """Main experiment controller (placeholder for expansion)."""

    def __init__(self, phase, stimuli):
        self.phase = phase
        self.stimuli = stimuli


# -------------------------------------------------------
# Main GUI
# -------------------------------------------------------

DEFAULT_FONT = ("Arial", 16)
helper = HelperFunctions(*DEFAULT_FONT)

root = Tk()
root.title("FFG-STIWA, Experiment 1.2")
root.geometry("400x400+50+150")

intro_message = Label(
    root,
    text="Please click on the instructions button\nand read the information carefully!",
    font=DEFAULT_FONT
)
intro_message.pack(pady=10)

instruction_btn = Button(
    root,
    text="Instruction",
    font=DEFAULT_FONT,
    command=lambda: helper.open_text_window(
        parent=root,
        title="Instruction",
        text="...",
        geometry="600x400+500+50"
    )
)
instruction_btn.pack(pady=10)

practice_btn = Button(
    root,
    text="Start Practice",
    font=DEFAULT_FONT,
    command=lambda: helper.open_practice_window(
        parent=root,
        title="Practice Session",
        geometry="600x400+500+50"
    )
)
practice_btn.pack(pady=10)

root.mainloop()
